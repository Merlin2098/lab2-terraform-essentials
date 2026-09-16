# Guía de despliegue — lab2-terraform-essentials

Instrucciones para ejecutar la infraestructura de este laboratorio (S3 + Lambda
CSV→Parquet) con Terraform.

## Prerrequisitos

* Terraform >= 1.6.0
* Credenciales AWS configuradas (`aws configure` o variables de entorno)
* Acceso a la región donde se desplegará (por defecto `us-east-1`)

## ARNs involucrados — no confundir

* **`lambda_pandas_layer_arn`** — **input obligatorio**, sin default. Debes
  obtenerlo *antes* de aplicar. Es el ARN de la layer administrada por AWS
  "AWS SDK for pandas" (provee pandas y pyarrow), específico de región y
  runtime.
* **`lambda_function_arn`** — **output** del proyecto. Es el ARN de la Lambda
  que este Terraform crea. No se necesita de antemano: se obtiene *después*
  de `terraform apply`.

## Flujo de ejecución

### 1. Obtener el ARN de la layer de pandas

Vía consola: AWS Console → Lambda → Layers → "Add a layer" → "AWS layers" →
`AWSSDKPandas-Python313` (debe coincidir con el runtime definido en
`lambda_runtime`, por defecto `python3.13`).

Vía CLI:

```bash
aws lambda list-layers --region us-east-1 \
  --query "Layers[?LayerName=='AWSSDKPandas-Python313']"
```

Copia el ARN completo, incluyendo la versión.

### 2. Configurar el backend remoto (opcional)

Copia `infra/backend.tf.example` a `infra/backend.tf` y completa el bucket y
key de estado. Si es solo un laboratorio local, puedes omitir este paso y
usar estado local.

### 3. Definir variables

Crea `infra/terraform.tfvars` (no se versiona) con al menos:

```hcl
lambda_pandas_layer_arn = "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python313:xx"
```

Agrega overrides opcionales si aplica: `project_name`, `environment`, `owner`,
`aws_region`, `cost_center`, `tags`, etc. (ver `infra/variables.tf`).

### 4. Ejecutar Terraform

Desde `infra/`:

```bash
terraform init
terraform plan
terraform apply
```

> `terraform apply` y `terraform destroy` requieren aprobación explícita del
> usuario — no se ejecutan de forma autónoma (ver `AGENTS.md`).

### 5. Obtener el ARN de la Lambda creada

Tras un `apply` exitoso:

```bash
terraform output lambda_function_arn
```

## Referencia de outputs disponibles

| Output | Descripción |
|---|---|
| `raw_bucket_name` / `raw_bucket_arn` | Bucket S3 donde se suben los CSV |
| `processed_bucket_name` / `processed_bucket_arn` | Bucket S3 con los Parquet transformados |
| `lambda_function_name` / `lambda_function_arn` | Lambda de transformación CSV→Parquet |
| `log_group_name` / `log_group_arn` | Log group de CloudWatch de la Lambda |
