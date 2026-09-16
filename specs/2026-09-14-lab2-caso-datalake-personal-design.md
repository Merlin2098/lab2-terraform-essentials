# Lab 2 — Caso: "Mi primer data lake personal"

## Contexto

Este lab es el primer contacto de un grupo de alumnos del bootcamp de Data
Analytics con Terraform. Los alumnos ya vieron la consola de AWS (saben crear
recursos manualmente) pero nunca usaron Infraestructura como Código. La
sesión tiene un alcance de 3-4 horas.

> **Revisión 2026-09-14 (v2):** se amplía el caso para introducir una segunda
> etapa — automatización de la transformación de datos vía Lambda — y se
> introduce el patrón de módulos de Terraform. La v1 (bucket + log group
> planos) queda como la primera mitad de la progresión pedagógica.

## Narrativa

El alumno está armando su propio mini data lake personal para practicar
análisis de datos. Sube archivos CSV a un bucket de datos crudos ("raw").
Quiere que, apenas suba un archivo, se transforme automáticamente a Parquet
(formato más eficiente para análisis) y quede disponible en un bucket de
datos procesados ("processed"), con un registro en logs de que el archivo
fue procesado — sin tener que hacer nada manual ni depender de clicks en la
consola AWS.

Se eligió una narrativa de proyecto personal (en lugar de una empresa o
equipo de analítica) para evitar la carga cognitiva de simular un contexto
de negocio, dado que los alumnos no tienen experiencia previa con Terraform.

## Servicios AWS involucrados

- **S3** (x2): bucket `raw` para aterrizar CSVs, bucket `processed` para los
  Parquet resultantes.
- **Lambda**: función que se dispara al subir un CSV a `raw`, lo convierte a
  Parquet y lo sube a `processed`.
- **IAM**: rol de ejecución de la Lambda con permisos mínimos (leer de
  `raw`, escribir en `processed`, escribir logs).
- **CloudWatch Logs**: log group de la Lambda, declarado explícitamente
  (retención controlada) en vez de dejarlo autogenerar — refuerza la
  política de observabilidad ya documentada en `ai/domains/terraform.md`.

## Dependencia de empaquetado: AWS SDK for pandas (Lambda Layer pública)

La transformación usa `pandas`/`pyarrow`, que no vienen en el runtime base
de Lambda y son demasiado pesados para empaquetar a mano en un `.zip` en un
lab de este alcance. Se resuelve referenciando la **Lambda Layer pública
"AWS SDK for pandas"** (ARN publicado por AWS por región/runtime) desde
Terraform — los alumnos no compilan ni empaquetan dependencias, solo
declaran el ARN de la layer como parte de la función.

## Qué se construye

```
infra/
  main.tf                  # instancia module "datalake"
  variables.tf             # variables del root
  outputs.tf                # re-expone outputs del módulo
  terraform.tfvars.example
  modules/
    datalake/
      main.tf              # buckets, lambda, iam, notification
      variables.tf
      outputs.tf
src/
  lambda/
    csv_to_parquet.py       # código de la función Lambda
  generator/
    generator.py            # genera CSVs random en data/ para probar el lab
data/
  *.csv                      # CSVs generados localmente, subidos a mano a "raw"
```

Se introduce `modules/datalake/` como primer módulo de Terraform del
proyecto — antes de esta revisión, `infra/` era intencionalmente un root
module plano (ver `ai/domains/terraform.md`: "infra/ is currently a single
flat root module... if that changes, module/promotion patterns belong back
here"). El salto de complejidad (2 buckets + Lambda + IAM + notificación)
justifica ahora ese cambio, y sirve como lección explícita del lab: pasar de
recursos sueltos a un módulo autocontenido.

El código de la Lambda vive en `src/lambda/` en la raíz del proyecto,
separado de la definición de infraestructura, siguiendo la separación
código/infra ya establecida en el repo.

1. **Bucket `raw`** (`aws_s3_bucket`) — recibe los CSV subidos por el
   alumno.
2. **Bucket `processed`** (`aws_s3_bucket`) — recibe los Parquet generados.
3. **Tags obligatorios** vía `local.common_tags` en ambos buckets y en la
   Lambda, incluyendo `CostCenter`.
4. **`aws_lambda_function.csv_to_parquet`** — runtime Python, usa la layer
   pública de AWS SDK for pandas. Código fuente: `src/lambda/csv_to_parquet.py`.
5. **IAM role + policy** de ejecución de la Lambda: `s3:GetObject` sobre
   `raw`, `s3:PutObject` sobre `processed`, permisos de CloudWatch Logs
   (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`).
6. **`aws_s3_bucket_notification`** en el bucket `raw` → invoca la Lambda en
   `s3:ObjectCreated:*`, filtrando por sufijo `.csv`.
7. **`aws_lambda_permission`** que autoriza a S3 a invocar la función.
8. **CloudWatch Log Group** explícito para `/aws/lambda/<nombre>`, con
   retención controlada por variable.
9. **Variables**: `aws_region`, `project_name`, `environment`, `owner`, y
   flags de versioning/force_destroy para ambos buckets, `log_retention_days`.
10. **Outputs**: ARNs/nombres de ambos buckets, ARN/nombre de la Lambda,
    `log_group_name` / `log_group_arn`.

### Código de la Lambda (`src/lambda/csv_to_parquet.py`)

Lógica mínima, con foco en que el alumno entienda el flujo (no en Python
avanzado):

1. Lee el evento S3 (bucket y key del CSV recién subido).
2. Descarga el CSV a `/tmp`.
3. `pandas.read_csv(...)` → `to_parquet(...)` (pandas + pyarrow de la
   layer).
4. Sube el Parquet resultante a `processed/` con el mismo nombre base.
5. `logger.info(...)` indicando qué archivo fue procesado — visible en
   CloudWatch Logs, es "la constancia de que se cargó el archivo".

### Script generador de datos (`src/generator/generator.py`)

Script Python que el alumno corre localmente (no se despliega a AWS) para
generar CSVs de datos aleatorios con los que probar el flujo, sin depender
de un dataset externo. Genera uno o más archivos `.csv` con datos ficticios
(ej. filas con id, nombre, fecha, valor numérico) y los guarda en `data/`
en la raíz del proyecto. El alumno luego sube manualmente esos CSVs al
bucket `raw` (por consola o `aws s3 cp`) para disparar la Lambda.

## Progresión pedagógica (3-4h)

**Primera mitad — fundamentos (sobre el módulo, no recursos sueltos):**

1. `terraform init` — entender providers y backend local.
2. Escribir el bucket `raw` mínimo dentro de `modules/datalake/` → `plan` →
   `apply` → verificar en consola AWS (conecta lo manual que ya conocen con
   lo declarativo). Ver cómo el root module solo instancia
   `module "datalake" { ... }`.
3. Agregar tags → volver a correr `plan` para observar el diff no
   destructivo.
4. Agregar el log group + outputs → segundo ciclo plan/apply.
5. Cambiar una variable (ej. `environment`) y observar cómo cambia el plan
   sin tocar código.

**Segunda mitad — automatización:**

6. Agregar el bucket `processed` y ver cómo el módulo devuelve dos ARNs de
   bucket distintos.
7. Escribir la Lambda (código provisto en `src/lambda/`, foco en Terraform
   no en Python) y su IAM role → primer `apply` con Lambda, referenciando la
   layer pública de AWS SDK for pandas.
8. Conectar `aws_s3_bucket_notification` + `aws_lambda_permission`.
9. Correr `src/generator/generator.py` para generar CSVs de prueba en
   `data/`, subir uno a `raw`, ver el Parquet aparecer en `processed`, y el
   log en CloudWatch confirmando el procesamiento.
10. Cierre: `terraform destroy` guiado, para entender el ciclo de vida
    completo y no dejar recursos huérfanos.

## Justificación de diseño

- La narrativa se mantiene (proyecto personal) para no agregar carga
  cognitiva de negocio sobre alumnos sin experiencia previa en Terraform.
- El módulo se introduce recién en este punto, cuando el número de recursos
  relacionados (2 buckets + Lambda + IAM + notificación) empieza a mezclar
  responsabilidades en un único archivo — consistente con la guía de no
  modularizar prematuramente que regía la v1.
- La layer pública de AWS SDK for pandas evita que el lab se convierta en un
  ejercicio de empaquetado de dependencias Python, que no es el objetivo
  (el objetivo es Terraform).
- El script generador (`src/generator/generator.py`) evita depender de un
  dataset externo o de que el alumno consiga sus propios CSVs; genera datos
  reproducibles bajo demanda para probar el flujo end-to-end.
- Separar `src/lambda/` de `infra/` mantiene la separación código/infra ya
  usada en el resto del repo.

## Referencias

- `infra/providers.tf`
- `infra/terraform.tfvars.example` (variables base ya definidas)
- `ai/domains/terraform.md` (política de observabilidad y governance;
  condición para introducir módulos)
- `AGENTS.md` (límites de aprobación: `terraform apply`/`destroy` requieren
  aprobación explícita del usuario)
