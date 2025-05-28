import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export class VpcStack extends cdk.Stack {
    public readonly vpc: ec2.Vpc;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create VPC
        this.vpc = new ec2.Vpc(this, 'AgentMarketplaceVpc', {
            maxAzs: 3,
            cidr: '10.0.0.0/16',
            subnetConfiguration: [
                {
                    cidrMask: 24,
                    name: 'public-subnet',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                    cidrMask: 24,
                    name: 'private-subnet',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
                },
                {
                    cidrMask: 24,
                    name: 'isolated-subnet',
                    subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                },
            ],
            natGateways: 1,
        });

        // Create Security Groups
        const webSg = new ec2.SecurityGroup(this, 'WebSecurityGroup', {
            vpc: this.vpc,
            description: 'Security group for web application',
            allowAllOutbound: true,
        });

        webSg.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(80),
            'Allow HTTP access from anywhere'
        );

        webSg.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(443),
            'Allow HTTPS access from anywhere'
        );

        // Create ALB Security Group
        const albSg = new ec2.SecurityGroup(this, 'AlbSecurityGroup', {
            vpc: this.vpc,
            description: 'Security group for ALB',
            allowAllOutbound: true,
        });

        albSg.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(80),
            'Allow HTTP access from anywhere'
        );

        albSg.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(443),
            'Allow HTTPS access from anywhere'
        );
    }
}
