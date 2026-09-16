# Lab 2 — Terraform Essentials: mi primer data lake personal

## ¿Qué es este laboratorio?

Este es tu primer contacto con **Terraform**, la herramienta más usada para
manejar infraestructura como código (Infrastructure as Code, o IaC). Hasta
ahora creaste recursos en AWS haciendo clic en la consola. Acá vas a
aprender a describir esos mismos recursos en archivos de texto, y dejar que
Terraform los cree, actualice o elimine por vos.

**¿Por qué importa esto?** Porque en el mundo real nadie levanta
infraestructura a mano, recurso por recurso, cada vez. Escribirla como
código te permite repetirla, versionarla, revisarla en equipo y destruirla
sin miedo cuando ya no la necesitás — algo clave quiere que quede claro
desde tu primera semana con AWS.

## El caso: tu data lake personal

Vas a construir, paso a paso, un mini data lake para practicar análisis de
datos:

1. Subís un archivo **CSV** a un bucket S3 (`raw`).
2. Eso dispara automáticamente una **función Lambda**.
3. La Lambda convierte el CSV a formato **Parquet** (más liviano y eficiente
   para análisis) y lo deja en otro bucket S3 (`processed`).
4. Cada vez que se procesa un archivo, queda un registro en **CloudWatch
   Logs** confirmando que se cargó.

Todo esto se crea, se modifica y se destruye con comandos de Terraform —
sin tocar la consola de AWS.

## Qué vas a aprender

- Los comandos base de Terraform: `init`, `plan`, `apply`, `destroy`.
- Cómo declarar recursos AWS (buckets S3, funciones Lambda, roles IAM,
  CloudWatch Logs) en archivos `.tf`.
- Qué son las **variables** y los **outputs**, y por qué te evitan repetir
  valores a mano.
- Qué es un **módulo** de Terraform y por qué conviene agrupar recursos
  relacionados en uno, en vez de tener todo suelto en un solo archivo.
- Cómo se conectan servicios de AWS entre sí (S3 → Lambda) sin escribir
  código de "pegamento" manual.

## Estructura del repositorio

```
infra/                      # Todo lo que define la infraestructura (Terraform)
  main.tf                    # Punto de entrada: instancia el módulo del data lake
  variables.tf                # Variables configurables (nombre de proyecto, región, etc.)
  outputs.tf                   # Valores que Terraform expone al terminar (ARNs, nombres)
  terraform.tfvars.example      # Ejemplo de valores para tus variables
  modules/
    datalake/                    # Módulo con los buckets, la Lambda, IAM y la conexión entre ellos

src/
  lambda/
    csv_to_parquet.py           # Código Python que corre dentro de la Lambda
  generator/
    generator.py                 # Script para generar CSVs de prueba

data/                        # Acá se guardan los CSVs que generás localmente
```

No necesitás editar el código Python para completar el lab — ya está
armado. Tu trabajo principal es escribir y entender el código Terraform en
`infra/`.

## Antes de empezar

1. Tener instalado **Terraform** (`terraform version` debería funcionar en
   tu terminal).
2. Tener credenciales de AWS configuradas (las mismas que usás para entrar
   a la consola, vía `aws configure` o variables de entorno).
3. Copiar `infra/terraform.tfvars.example` a `infra/terraform.tfvars` y
   revisar los valores — en particular, **verificar el ARN de la Lambda
   Layer de pandas** para tu región (se explica dentro del archivo).

## Cómo se corre

Todos los comandos de Terraform se ejecutan **desde la carpeta `infra/`**:

```bash
cd infra
terraform init      # Descarga los plugins necesarios (solo la primera vez)
terraform plan       # Muestra qué va a crear/cambiar, sin hacerlo todavía
terraform apply       # Aplica esos cambios en tu cuenta de AWS
```

Para generar un CSV de prueba y subirlo al data lake:

```bash
python src/generator/generator.py
aws s3 cp data/<archivo>.csv s3://<nombre-del-bucket-raw>/
```

El nombre del bucket lo obtenés con `terraform output raw_bucket_name`
después de aplicar. Revisá CloudWatch Logs y el bucket `processed` para
confirmar que el archivo fue transformado.

Al terminar el laboratorio, **no dejes recursos corriendo en tu cuenta**:

```bash
terraform destroy
```

> ⚠️ `terraform apply` y `terraform destroy` modifican recursos reales en
> AWS (y pueden generar costos). Corré `terraform plan` primero siempre que
> tengas dudas sobre lo que va a pasar.

## Progresión sugerida (3-4 horas)

El laboratorio está pensado para avanzar en dos mitades:

**Primera mitad — fundamentos:** crear el bucket `raw`, agregar tags,
agregar un log group, cambiar una variable y ver cómo cambia el plan.

**Segunda mitad — automatización:** agregar el bucket `processed`, la
función Lambda, conectarla al bucket `raw`, y probar el flujo completo
subiendo un CSV generado por vos.

El detalle completo de esta progresión, y las decisiones de diseño detrás
del caso, están documentados en
[`specs/2026-09-14-lab2-caso-datalake-personal-design.md`](specs/2026-09-14-lab2-caso-datalake-personal-design.md).

## Si algo sale mal

- Si `terraform apply` falla, leé el mensaje de error completo — casi
  siempre indica qué recurso y qué atributo está mal.
- Si te quedaste con recursos que no sabés de dónde salieron, corré
  `terraform plan` para ver qué detecta Terraform antes de tocar nada a
  mano en la consola.
- Preguntale a tu instructor antes de correr `terraform destroy` si no
  estás seguro de qué va a eliminar.
