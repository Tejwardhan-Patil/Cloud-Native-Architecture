provider "aws" {
  region = "us-east-1"
}

resource "aws_launch_configuration" "app" {
  name          = "app-launch-configuration"
  image_id      = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  security_groups = [aws_security_group.app.id]
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "app" {
  availability_zones   = ["us-east-1a", "us-east-1b", "us-east-1c"]
  desired_capacity     = 2
  max_size             = 5
  min_size             = 1
  health_check_grace_period = 300
  health_check_type    = "EC2"
  launch_configuration = aws_launch_configuration.app.id
  vpc_zone_identifier  = [aws_subnet.app[*].id]
  target_group_arns    = [aws_lb_target_group.app.arn]
  
  tag {
    key                 = "Name"
    value               = "app-instance"
    propagate_at_launch = true
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "app" {
  name        = "app-security-group"
  description = "Allow inbound traffic to the app"
  vpc_id      = aws_vpc.app.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "app" {
  name               = "app-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = aws_subnet.app[*].id
  
  enable_deletion_protection = false
}

resource "aws_lb_target_group" "app" {
  name     = "app-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.app.id

  health_check {
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up-policy"
  scaling_adjustment      = 1
  adjustment_type         = "ChangeInCapacity"
  cooldown                = 300
  autoscaling_group_name  = aws_autoscaling_group.app.name
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "scale-down-policy"
  scaling_adjustment      = -1
  adjustment_type         = "ChangeInCapacity"
  cooldown                = 300
  autoscaling_group_name  = aws_autoscaling_group.app.name
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "This alarm will trigger if CPU utilization exceeds 75%."

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_up.arn]
  ok_actions    = [aws_autoscaling_policy.scale_down.arn]
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
  alarm_name          = "low-cpu-utilization"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "25"
  alarm_description   = "This alarm will trigger if CPU utilization falls below 25%."

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_down.arn]
}

resource "aws_vpc" "app" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "app" {
  count = 3
  vpc_id            = aws_vpc.app.id
  cidr_block        = cidrsubnet(aws_vpc.app.cidr_block, 8, count.index)
  availability_zone = element(["us-east-1a", "us-east-1b", "us-east-1c"], count.index)
}

resource "aws_security_group" "lb" {
  name        = "lb-security-group"
  description = "Allow inbound traffic to the load balancer"
  vpc_id      = aws_vpc.app.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}