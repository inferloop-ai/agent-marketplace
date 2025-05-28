import * as cdk from 'aws-cdk-lib';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface DatabaseStackProps extends cdk.StackProps {
    vpc: ec2.Vpc;
}

export class DatabaseStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: DatabaseStackProps) {
        super(scope, id, props);

        // Create RDS security group
        const rdsSg = new ec2.SecurityGroup(this, 'RdsSecurityGroup', {
            vpc: props.vpc,
            description: 'Security group for RDS',
            allowAllOutbound: true,
        });

        // Allow inbound access from ECS security group
        rdsSg.addIngressRule(
            ec2.Peer.ipv4(props.vpc.vpcCidrBlock),
            ec2.Port.tcp(5432),
            'Allow PostgreSQL access from VPC'
        );

        // Create RDS instance
        const database = new rds.DatabaseInstance(this, 'AgentMarketplaceDatabase', {
            engine: rds.DatabaseInstanceEngine.postgres({
                version: rds.PostgresEngineVersion.VER_14_7,
            }),
            instanceType: ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL
            ),
            vpc: props.vpc,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
            },
            securityGroups: [rdsSg],
            allocatedStorage: 20,
            databaseName: 'agent_marketplace',
            credentials: rds.Credentials.fromGeneratedSecret('postgres'),
            deletionProtection: true,
            backupRetention: cdk.Duration.days(7),
            publiclyAccessible: false,
            multiAz: true,
        });

        // Create ElastiCache Redis cluster
        const redisSg = new ec2.SecurityGroup(this, 'RedisSecurityGroup', {
            vpc: props.vpc,
            description: 'Security group for Redis',
            allowAllOutbound: true,
        });

        redisSg.addIngressRule(
            ec2.Peer.ipv4(props.vpc.vpcCidrBlock),
            ec2.Port.tcp(6379),
            'Allow Redis access from VPC'
        );

        const redis = new rds.CfnDBCluster(this, 'RedisCluster', {
            engine: 'redis',
            cacheNodeType: 'cache.t3.small',
            numCacheNodes: 1,
            vpcSecurityGroupIds: [redisSg.securityGroupId],
            subnetGroupName: 'redis-subnet-group',
            autoMinorVersionUpgrade: true,
            engineVersion: '6.x',
        });

        // Create OpenSearch cluster
        const opensearchSg = new ec2.SecurityGroup(this, 'OpenSearchSecurityGroup', {
            vpc: props.vpc,
            description: 'Security group for OpenSearch',
            allowAllOutbound: true,
        });

        opensearchSg.addIngressRule(
            ec2.Peer.ipv4(props.vpc.vpcCidrBlock),
            ec2.Port.tcp(443),
            'Allow OpenSearch access from VPC'
        );

        const opensearch = new rds.CfnDBCluster(this, 'OpenSearchCluster', {
            domainName: 'agent-marketplace-opensearch',
            engineVersion: 'OpenSearch_1.3',
            nodeToNodeEncryptionEnabled: true,
            vpcSecurityGroupIds: [opensearchSg.securityGroupId],
            subnetIds: props.vpc.privateSubnets.map(subnet => subnet.subnetId),
            encryptionAtRestEnabled: true,
        });
    }
}
