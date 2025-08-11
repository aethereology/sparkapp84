terraform {
  required_version = ">= 1.5.0"
  required_providers { google = { source = "hashicorp/google", version = "~> 5.30.0" } }
}
provider "google" { project = var.project_id region = var.region }
resource "google_compute_network" "spark_vpc" { name = "spark-vpc" auto_create_subnetworks = false }
resource "google_compute_subnetwork" "spark_subnet" {
  name = "spark-subnet" ip_cidr_range = "10.10.0.0/24" region = var.region
  network = google_compute_network.spark_vpc.id purpose = "PRIVATE_RFC_1918"
}
resource "google_vpc_access_connector" "serverless_connector" {
  name = "spark-serverless-connector" region = var.region network = google_compute_network.spark_vpc.name ip_cidr_range = "10.8.0.0/28"
}
resource "google_redis_instance" "redis" {
  name = "spark-redis" memory_size_gb = 1 region = var.region tier = "BASIC"
  authorized_network = google_compute_network.spark_vpc.id connect_mode = "PRIVATE_SERVICE_ACCESS"
}
resource "google_storage_bucket" "public" {
  name = var.bucket_public location = var.region uniform_bucket_level_access = true
  lifecycle_rule { condition { age = 365 } action { type = "Delete" } }
}
resource "google_storage_bucket" "secure" {
  name = var.bucket_secure location = var.region uniform_bucket_level_access = true
  lifecycle_rule { condition { age = 365 } action { type = "SetStorageClass" storage_class = "NEARLINE" } }
}
output "memorystore_ip" { value = google_redis_instance.redis.host }
output "vpc_connector" { value = google_vpc_access_connector.serverless_connector.name }
variable "project_id" {} variable "region" { default = "us-central1" }
variable "bucket_public" { default = "spark-public" } variable "bucket_secure" { default = "spark-secure" }
