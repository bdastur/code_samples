provider "aws" {
  region                  = var.region 
  shared_credentials_files = var.credentials_files
  profile                 = var.profile 
}


locals {
  # Create metrics array dynamically
  metrics = concat(
    [["testnamespace", "TotalMetricCount", "accountId", var.account_ids[0]]],
    [for i, account_id in slice(var.account_ids, 1, length(var.account_ids)) : ["...", account_id]]
  )
}


resource "aws_cloudwatch_dashboard" "test_dashboard" {
  dashboard_name = "TestMetricDashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 18
        height = 3
        properties = {
          metrics = local.metrics
          sparkline = true
          view      = "singleValue"
          region    = "us-east-1"
          period    = 900
          stat      = "Average"
        }
      }
    ]
  })
}

# Output the dashboard URL for easy access
output "dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${aws_cloudwatch_dashboard.test_dashboard.dashboard_name}"
}

output "dashboard_name" {
  description = "CloudWatch Dashboard Name"
  value       = aws_cloudwatch_dashboard.test_dashboard.dashboard_name
}
