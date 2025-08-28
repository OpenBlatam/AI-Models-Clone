variable "cidr_block" { default = "10.0.0.0/16" }
variable "public_subnet_cidr" { default = "10.0.1.0/24" }
variable "az" { default = "us-east-1a" }
variable "tags" { type = map(string) } 