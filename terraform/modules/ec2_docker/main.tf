resource "aws_instance" "docker_host" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
  key_name      = var.key_name

  vpc_security_group_ids = [var.security_group_id]
  associate_public_ip_address = true

  tags = merge(
    var.tags,
    {
      Name = var.name
    }
  )

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    docker_compose_url = var.docker_compose_url
    repo_url           = var.repo_url
    branch             = var.branch
    compose_file       = var.compose_file
    feature_path       = var.feature_path
  })
}

resource "aws_eip" "public_ip" {
  instance = aws_instance.docker_host.id
  vpc      = true
}

output "public_ip" {
  value = aws_eip.public_ip.public_ip
} 