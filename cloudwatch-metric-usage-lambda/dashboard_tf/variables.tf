###########################################################
# Common Variables
###########################################################
variable "credentials_files" {
  type    = list 
  default = ["$HOME/.aws/credentials"]
}

variable "profile" {
  type    = string
}

variable "region" {
  type    = string
}

variable "account_ids" {
  description = "List of AWS account IDs to monitor"
  type        = list(string)
  default     = ["000000000067", "100000000030", "200000000053"]
}


