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
3. La Lambda valida y **normaliza** el CSV (encabezados en minúscula/snake_case,
   valores sin espacios sobrantes) usando solo la librería estándar de
   Python — sin Lambda layers — y deja el resultado en otro bucket S3
   (`processed`).
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
  relacionados en uno, en vez de tener todo suelto en un solo archivo, y
  cuándo separarlos en módulos independientes (S3 vs. Lambda) para
  mantenerlos enfocados en una sola responsabilidad.
- Cómo se conectan servicios de AWS entre sí (S3 → Lambda) sin escribir
  código de "pegamento" manual.

## Estructura del repositorio

```
infra/                          # Todo lo que define la infraestructura (Terraform)
  main.tf                        # Punto de entrada: instancia los módulos del data lake
  variables.tf                    # Variables configurables (nombre de proyecto, región, etc.)
  outputs.tf                       # Valores que Terraform expone al terminar (ARNs, nombres)
  terraform.tfvars.example          # Ejemplo de valores para tus variables
  backend.tf.example                 # Ejemplo de configuración de backend remoto (opcional)
  modules/
    s3-datalake/                      # Buckets raw y processed (versioning, cifrado, bloqueo público)
    lambda-csv-normalizer/             # Función Lambda, rol/policy IAM, log group y notificación S3

src/
  lambda/
    csv_normalizer.py               # Código Python que corre dentro de la Lambda
  generator/
    generator.py                     # Script para generar CSVs de prueba

scripts/
  aws/
    upload_data_to_raw.py           # Sube los CSV de data/ al bucket raw y descarga los logs de la Lambda
  python/
    setup_env.sh / setup_env.ps1     # Crea el entorno virtual (.venv)
    update_venv.sh / update_venv.ps1  # Instala/actualiza dependencias desde requirements*.txt

data/                            # Acá se guardan los CSVs que generás o cargás localmente
logs/                            # Logs de CloudWatch descargados por scripts/aws/upload_data_to_raw.py
```

No necesitás editar el código Python para completar el lab — ya está
armado. Tu trabajo principal es escribir y entender el código Terraform en
`infra/`.

## Antes de empezar

1. Tener instalado **Terraform** (`terraform version` debería funcionar en
   tu terminal).
2. Tener credenciales de AWS configuradas. Copiá `.env.example` a
   `.env.credentials` en la raíz del proyecto y completá tus valores reales
   (nunca comitees ese archivo). El detalle completo de este paso está en
   [`docs/deploy-guide.md`](docs/deploy-guide.md).
3. Copiar `infra/terraform.tfvars.example` a `infra/terraform.tfvars` si
   querés sobrescribir algún default (no es obligatorio: no hay variables
   sin default en este proyecto).
4. Crear el entorno virtual de Python e instalar dependencias:

   ```bash
   ./scripts/python/setup_env.sh
   ./scripts/python/update_venv.sh
   ```

## Cómo generar datasets de prueba

`src/generator/generator.py` genera CSVs aleatorios en `data/` (columnas
`id`, `name`, `signup_date`, `amount`), listos para cargar al data lake.
Cada archivo se guarda como `data/orders_<id-aleatorio>.csv`.

```bash
python src/generator/generator.py                    # 1 archivo, 100 filas (default)
python src/generator/generator.py --rows 500          # 1 archivo, 500 filas
python src/generator/generator.py --files 3 --rows 50 # 3 archivos, 50 filas cada uno
```

También podés poner tus propios CSVs en `data/` manualmente — el pipeline
no depende del generador, solo espera un CSV con encabezado.

## Cómo se corre

Todos los comandos de Terraform se ejecutan **desde la carpeta `infra/`**:

```bash
cd infra
terraform init      # Descarga los plugins necesarios (solo la primera vez)
terraform plan       # Muestra qué va a crear/cambiar, sin hacerlo todavía
terraform apply       # Aplica esos cambios en tu cuenta de AWS
```

Para generar un CSV de prueba, cargarlo al data lake y validar el pipeline
completo (desde la raíz del proyecto):

```bash
python src/generator/generator.py
python scripts/aws/upload_data_to_raw.py
```

`upload_data_to_raw.py` sube todos los CSV de `data/` al bucket `raw`
(resuelto automáticamente vía `terraform output`), espera a que la Lambda
los procese, y descarga el log de CloudWatch de esa ejecución a `logs/`.
Más detalle en el paso 6 de [`docs/deploy-guide.md`](docs/deploy-guide.md).

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

## Si algo sale mal

- Si `terraform apply` falla, leé el mensaje de error completo — casi
  siempre indica qué recurso y qué atributo está mal.
- Si te quedaste con recursos que no sabés de dónde salieron, corré
  `terraform plan` para ver qué detecta Terraform antes de tocar nada a
  mano en la consola.
- Preguntale a tu instructor antes de correr `terraform destroy` si no
  estás seguro de qué va a eliminar.
