# Guía de despliegue — lab2-terraform-essentials

Instrucciones para ejecutar la infraestructura de este laboratorio (S3 + Lambda
de normalización de CSV) con Terraform.

## Prerrequisitos

* Terraform >= 1.6.0
* Credenciales AWS configuradas (`aws configure` o variables de entorno)
* Acceso a la región donde se desplegará (por defecto `us-east-1`)

## ARN involucrado

* **`lambda_function_arn`** — **output** del proyecto. Es el ARN de la Lambda
  que este Terraform crea. No se necesita de antemano: se obtiene *después*
  de `terraform apply`.

La Lambda usa únicamente la librería estándar de Python (`csv`, `io`), por lo
que no requiere ninguna Lambda layer ni ARN externo para funcionar.

## Flujo de ejecución

### 1. Configurar credenciales AWS como variables de entorno

Copia `.env.example` a `.env.credentials` en la raíz del proyecto y reemplaza
los valores por tus credenciales reales. Nunca comitees ese archivo.

```bash
cp .env.example .env.credentials
# edita .env.credentials con tus valores reales
```

Carga las variables en la sesión de terminal actual:

**Git Bash:**

```bash
set -a
source .env.credentials
set +a
```

**PowerShell:**

```powershell
Get-Content .env.credentials | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $name, $value = $_ -split '=', 2
    Set-Item -Path "env:$name" -Value $value
}
```

Verifica que las credenciales quedaron activas:

```bash
aws sts get-caller-identity
```

> Estas variables solo persisten en la sesión de terminal actual. Si abres
> una nueva ventana/pestaña, debes volver a repetir el `source` (Git Bash) o
> el bloque `Set-Item` (PowerShell).

### 2. Configurar el backend remoto (opcional)

Copia `infra/backend.tf.example` a `infra/backend.tf` y completa el bucket y
key de estado. Si es solo un laboratorio local, puedes omitir este paso y
usar estado local.

### 3. Definir variables (opcional)

Crea `infra/terraform.tfvars` (no se versiona) solo si quieres sobrescribir
defaults: `project_name`, `environment`, `owner`, `aws_region`, `cost_center`,
`tags`, etc. (ver `infra/variables.tf`). No hay variables obligatorias sin
default en este proyecto.

### 4. Flujo de Terraform

Todos los comandos se ejecutan **desde `infra/`**.

```bash
cd infra
```

1. **`terraform init`** — inicializa el working directory, descarga
   providers (`aws`, `archive`) y configura el backend.

   ```bash
   terraform init
   ```
2. **`terraform fmt`** — normaliza el formato de los ficheros `.tf`.
   Usa `-recursive` para incluir el módulo `modules/datalake`.

   ```bash
   terraform fmt -recursive
   ```
3. **`terraform validate`** — valida sintaxis y coherencia interna
   (tipos, referencias) sin tocar AWS.

   ```bash
   terraform validate
   ```
4. **`terraform plan`** — genera el plan de cambios contra el estado
   actual. Revisa siempre la salida antes de aplicar.

   ```bash
   terraform plan
   ```
5. **`terraform apply`** — aplica el plan y crea/actualiza los recursos
   en AWS.

   ```bash
   terraform apply
   ```

   > Requiere aprobación explícita del usuario antes de ejecutarse — no se
   > ejecuta de forma autónoma (ver `AGENTS.md`).
   >
6. **`terraform destroy`** — elimina todos los recursos gestionados por
   este estado. Úsalo solo para limpiar el laboratorio.

   ```bash
   terraform destroy
   ```

   > Igual que `apply`, requiere aprobación explícita del usuario y nunca se
   > ejecuta sin confirmación previa (ver `AGENTS.md`).
   >

### 5. Obtener el ARN de la Lambda creada

Tras un `apply` exitoso:

```bash
terraform output lambda_function_arn
```

## Referencia de outputs disponibles

| Output | Descripción |
| --- | --- |
| `raw_bucket_name` / `raw_bucket_arn` | Bucket S3 donde se suben los CSV |
| `processed_bucket_name` / `processed_bucket_arn` | Bucket S3 con los CSV normalizados |
| `lambda_function_name` / `lambda_function_arn` | Lambda de normalización de CSV |
| `log_group_name` / `log_group_arn` | Log group de CloudWatch de la Lambda |
