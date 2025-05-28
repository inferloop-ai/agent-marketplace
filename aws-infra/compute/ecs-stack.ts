import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import { Construct } from 'constructs';

export interface EcsStackProps extends cdk.StackProps {
    vpc: ec2.Vpc;
}

export class EcsStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: EcsStackProps) {
        super(scope, id, props);

        // Create ECS cluster
        const cluster = new ecs.Cluster(this, 'AgentMarketplaceCluster', {
            vpc: props.vpc,
            clusterName: 'agent-marketplace-cluster',
        });

        // Create ECS task definition
        const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
            memoryLimitMiB: 4096,
            cpu: 2048,
        });

        // Add container to task definition
        taskDefinition.addContainer('AgentMarketplaceContainer', {
            image: ecs.ContainerImage.fromRegistry('agent-marketplace:latest'),
            memoryLimitMiB: 4096,
            logging: ecs.LogDriver.awsLogs({
                streamPrefix: 'agent-marketplace',
            }),
            environment: {
                DATABASE_URL: process.env.DATABASE_URL || '',
                OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
            },
        });

        // Create ECS service
        const service = new ecs.FargateService(this, 'AgentMarketplaceService', {
            cluster,
            taskDefinition,
            desiredCount: 2,
            serviceName: 'agent-marketplace-service',
            assignPublicIp: true,
        });

        // Create ALB
        const alb = new elbv2.ApplicationLoadBalancer(this, 'AgentMarketplaceALB', {
            vpc: props.vpc,
            internetFacing: true,
        });

        // Create listener
        const listener = alb.addListener('HttpListener', {
            port: 80,
        });

        // Add target group
        const targetGroup = listener.addTargets('EcsTargetGroup', {
            port: 80,
            targets: [service],
            healthCheck: {
                path: '/health',
                interval: cdk.Duration.seconds(30),
                timeout: cdk.Duration.seconds(5),
            },
        });

        // Add HTTPS listener
        const httpsListener = alb.addListener('HttpsListener', {
            port: 443,
            certificates: [], // Add your SSL certificates here
        });

        httpsListener.addTargetGroups('HttpsTargetGroup', {
            targetGroups: [targetGroup],
        });
    }
}
