variable "ami_id" {}
variable "instance_type" { default = "t3.medium" }
variable "subnet_id" {}
variable "key_name" {}
variable "security_group_id" {}
variable "tags" { type = map(string) }
variable "name" {}
variable "docker_compose_url" { default = "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64" }
variable "repo_url" {}
variable "branch" { default = "main" }
variable "compose_file" { default = "docker-compose.yml" }
variable "feature_path" { description = "Ruta al feature dentro del repo" } 