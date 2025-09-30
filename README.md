# clicknumber - serviço de ping aleatório

Este projeto oferece um serviço simples que realiza requisições HTTP repetidas a uma mesma URL em intervalos aleatórios entre 1 e 3 segundos (configuráveis). Pode ser executado localmente ou em um container Docker, o que facilita o deploy em provedores como a DigitalOcean.

## Como funciona
- Lê a URL de destino da variável de ambiente `TARGET_URL`.
- Envia requisições HTTP (método padrão `GET`) utilizando o pacote `requests`.
- Entre cada requisição aguarda um intervalo aleatório entre `MIN_INTERVAL` e `MAX_INTERVAL` segundos.
- Registra logs com o status da requisição e tempo de resposta.
- Trata sinais de encerramento (`SIGINT`/`SIGTERM`) para desligar de forma limpa.

## Variáveis de ambiente
| Variável           | Padrão | Descrição |
|-------------------|--------|-----------|
| `TARGET_URL`      | URL padrão indicada abaixo | URL a ser acessada repetidamente. Quando não definida, utiliza `https://camo.githubusercontent.com/6279ae4e6a1047e5bf8fca8f257562d182f64c83def68a33c2d26b295fd54fad/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d726f647269676f616e746f6e696f6c69267374796c653d666c6174`. |
| `MIN_INTERVAL`    | `1.0`  | Intervalo mínimo (segundos) entre requisições. |
| `MAX_INTERVAL`    | `3.0`  | Intervalo máximo (segundos) entre requisições. |
| `REQUEST_TIMEOUT` | `5.0`  | Tempo máximo de espera em cada requisição. |
| `HTTP_METHOD`     | `GET`  | Método HTTP utilizado. |
| `LOG_LEVEL`       | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, ...). |

Se quiser usar diretamente a URL padrão acima, basta não definir `TARGET_URL` ao iniciar o serviço.

## Executando localmente (Python)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TARGET_URL="https://exemplo.com"
python main.py
```

## Executando com Docker
```bash
docker build -t clicknumber .
docker run --rm \
  -e TARGET_URL="https://exemplo.com" \
  -e MIN_INTERVAL=1 \
  -e MAX_INTERVAL=3 \
  clicknumber
```

## Deploy em uma Droplet (DigitalOcean)
1. Crie uma Droplet com Ubuntu ou outra distro de sua preferência.
2. Instale o Docker na Droplet (ex.: `curl -fsSL https://get.docker.com | sh`).
3. Faça login na Droplet e clone este repositório (ou envie os arquivos via `scp`).
4. Dentro da pasta do projeto, construa a imagem: `docker build -t clicknumber .`.
5. Execute o container em segundo plano: 
   ```bash
   docker run -d \
     --name clicknumber \
     -e TARGET_URL="https://exemplo.com" \
     -e MIN_INTERVAL=1 \
     -e MAX_INTERVAL=3 \
     clicknumber
   ```
6. Visualize os logs quando quiser: `docker logs -f clicknumber`.

### Mantendo o serviço ativo após reboot
Você pode usar `docker run --restart=always` para garantir que o container seja reiniciado automaticamente:
```bash
docker run -d \
  --name clicknumber \
  --restart=always \
  -e TARGET_URL="https://exemplo.com" \
  clicknumber
```

## Parando o serviço
- Python local: `Ctrl + C`.
- Docker: `docker stop clicknumber`.

## Desenvolvimento
Para rodar o formatter/linters ou testes personalizados basta instalar as dependências extras que desejar e adaptar o workflow. Este projeto foi mantido propositalmente enxuto para focar no comportamento principal.
