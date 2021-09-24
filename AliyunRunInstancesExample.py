#!/usr/bin/env python
# coding=utf-8
import json
import time
import traceback

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest


RUNNING_STATUS = 'Running'
CHECK_INTERVAL = 3
CHECK_TIMEOUT = 180


class AliyunRunInstancesExample(object):

    def __init__(self):
        self.access_id = '<AccessKey>'
        self.access_secret = '<AccessSecret>'

        # Whether to send a pre-check only request. If this is set to true, a pre-check only request will be sent, no instance will be created, and no fees will be generated. If this is set to false, a normal request will be sent. For normal requests, after the pre-check is passed, an instance will be created and fees will be generated.
        self.dry_run = False
        # The region ID
        self.region_id = 'cn-beijing'
        # The instance type
        self.instance_type = 'ecs.t5-lc2m1.nano'
        # The billing method of the instance
        self.instance_charge_type = 'PostPaid'
        # The image ID stored in AliCloud
        self.image_id = '<ImageID>'
        # The security group to which the instances belongs
        self.security_group_id = '<GroupID>'
        # The period of the subscription, how many hours to run
        self.period = 1
        # The unit of the subscription period
        self.period_unit = 'Hourly'
        # The zone ID
        self.zone_id = 'random'
        # The billing method of the network bandwidth
        self.internet_charge_type = 'PayByTraffic'
        # The VSwitch ID
        self.vswitch_id = '<VSwitchID>'
        # The instance name
        self.instance_name = '<InstanceName>'
        # The number of instances you want to create
        self.amount = 1
        # The maximum outbound bandwidth to the Internet
        self.internet_max_bandwidth_out = 5
        # Whether the instance is I/O-optimized
        self.io_optimized = 'optimized'
        # The name of the key pair stored in AliCloud
        self.key_pair_name = '<KeyPair>'
        # The size of the system disk
        self.system_disk_size = '40'
        # The type of the system disk
        self.system_disk_category = 'cloud_efficiency'
        
        self.client = AcsClient(self.access_id, self.access_secret, self.region_id)

    def run(self):
        try:
            ids = self.run_instances()
            self._check_instances_status(ids)
        except ClientException as e:
            print('Fail. Something with your connection with Aliyun go incorrect.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except ServerException as e:
            print('Fail. Business error.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except Exception:
            print('Unhandled error')
            print(traceback.format_exc())

    def run_instances(self):
        """
        Calling the instance creation API, and querying the instance status after the instance ID is retrieved.
        :return:instance_ids The ID of the instance that needs to be checked
        """
        request = RunInstancesRequest()
       
        request.set_DryRun(self.dry_run)
        
        request.set_InstanceType(self.instance_type)
        request.set_InstanceChargeType(self.instance_charge_type)
        request.set_ImageId(self.image_id)
        request.set_SecurityGroupId(self.security_group_id)
        request.set_Period(self.period)
        request.set_PeriodUnit(self.period_unit)
        request.set_ZoneId(self.zone_id)
        request.set_InternetChargeType(self.internet_charge_type)
        request.set_VSwitchId(self.vswitch_id)
        request.set_InstanceName(self.instance_name)
        request.set_Amount(self.amount)
        request.set_InternetMaxBandwidthOut(self.internet_max_bandwidth_out)
        request.set_IoOptimized(self.io_optimized)
        request.set_KeyPairName(self.key_pair_name)
        request.set_SystemDiskSize(self.system_disk_size)
        request.set_SystemDiskCategory(self.system_disk_category)
         
        body = self.client.do_action_with_exception(request)
        data = json.loads(body)
        instance_ids = data['InstanceIdSets']['InstanceIdSet']
        print('Success. Instance creation succeed. InstanceIds: {}'.format(', '.join(instance_ids)))
        return instance_ids

    def _check_instances_status(self, instance_ids):
        """
        Checking the instance status every 3 seconds within 3 minutes
        :param instance_ids The ID of the instance that needs to be checked
        :return:
        """
        start = time.time()
        while True:
            request = DescribeInstancesRequest()
            request.set_InstanceIds(json.dumps(instance_ids))
            body = self.client.do_action_with_exception(request)
            data = json.loads(body)
            for instance in data['Instances']['Instance']:
                if RUNNING_STATUS in instance['Status']:
                    instance_ids.remove(instance['InstanceId'])
                    print('Instance boot successfully: {}'.format(instance['InstanceId']))

            if not instance_ids:
                print('Instances all boot successfully')
                break

            if time.time() - start > CHECK_TIMEOUT:
                print('Instances boot failed within {timeout}s: {ids}'
                      .format(timeout=CHECK_TIMEOUT, ids=', '.join(instance_ids)))
                break

            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    AliyunRunInstancesExample().run()