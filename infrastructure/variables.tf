variable "location" {
  description = "The Azure Region to deploy resources"
  type        = string
  default     = "East US" 
}

variable "project_prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "shopsmart" 
}

# THE FIX: We are adding the environment variable here
variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
}