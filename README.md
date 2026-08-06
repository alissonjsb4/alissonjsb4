<h1 align="center">Alisson Jaime</h1>

<p align="center">
  <b>Engenharia de Computação — UFC · Fortaleza, Brasil</b><br>
  Construo sistemas de ponta a ponta: do circuito ao pipeline de dados que mede o circuito.
</p>

---

## Sobre

Trabalho nas duas pontas da mesma linha. Projeto hardware — RTL, FPGA, firmware — e
escrevo o software que valida, automatiza e analisa o que esse hardware produz. A
maior parte dos meus projetos vive no encontro dos dois: uma bancada de teste
controlada por Python, um modelo de ML rodando embarcado, um pipeline que cruza
séries de sensores para achar divergência.

Gosto especialmente de **automação com propósito** — sistema que roda sozinho,
guarda a série histórica e só chama sua atenção quando tem motivo.

Hoje sou bolsista de P&D em projeto financiado pela **EMBRAPII/SEBRAE**, coautor de
artigos publicados no **IEEE**, e fundador e presidente do capítulo **IEEE CASS** da UFC.

---

## Software, dados e automação

<table width="100%">
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/flight-watch">flight-watch</a></h3>
<p>Monitor de preços que roda de hora em hora, guarda a série histórica e notifica
apenas quando o preço atravessa uma faixa. <b>636 execuções autônomas e 5 alertas
enviados</b> — a supressão de ruído é o ponto do projeto.</p>
<sub><b>Stack:</b> Python · Playwright · pandas · API do Telegram · agendamento</sub>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/ecg-anomaly-detection">ecg-anomaly-detection</a></h3>
<p>Detector de batimentos anômalos treinado <b>só com exemplos normais</b>.
Mahalanobis, PCA e métricas escritos do zero em NumPy — sem scikit-learn.
<b>F1 0,944 e AUC 0,962</b>, reproduzível em 13 segundos.</p>
<sub><b>Stack:</b> Python · NumPy · SciPy · pandas · matplotlib</sub>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/pdi-deteccao-placas-esp32">pdi-deteccao-placas-esp32</a></h3>
<p>Detecção de placas veiculares com <b>MobileNetV1 rodando embarcado</b> num
ESP32-S3. Treinamento em Python, inferência em C++ dentro do microcontrolador — ML
onde a memória é medida em kilobytes.</p>
<sub><b>Stack:</b> Python · TensorFlow · C++ · ESP32-S3</sub>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/biruleibe">biruleibe</a></h3>
<p>Aplicação web em Streamlit para gerenciar ficha de RPG — estado persistido em
JSON, interface própria. Utilitário pequeno, feito porque eu precisava dele.</p>
<sub><b>Stack:</b> Python · Streamlit</sub>
</td>
</tr>
</table>

## Hardware e sistemas de baixo nível

<table width="100%">
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/8-bit-cpu-and-assembler-toolchain">CPU de 8 bits + toolchain</a></h3>
<p>Um computador inteiro do zero: CPU de 8 bits com ISA própria em Verilog e o
assembler correspondente em C++. Arquitetura de computadores, projeto RTL e
co-design hardware/software na mesma peça.</p>
<sub><b>Stack:</b> Verilog · C++ · Assembly</sub>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/simple-os-x86">simple-os-x86</a></h3>
<p>Sistema operacional de 16 bits para x86 escrito em Assembly — bootloader, kernel
e editor de texto, conversando direto com o hardware via interrupções de BIOS.</p>
<sub><b>Stack:</b> x86 Assembly</sub>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/stm32-lora-telemetry-relay">stm32-lora-telemetry-relay</a></h3>
<p>Firmware de dois nós STM32 formando um enlace de telemetria de longo alcance por
LoRa, com captura UART por DMA e validação por máquina de estados.</p>
<sub><b>Stack:</b> C · STM32 HAL · LoRa · DMA</sub>
</td>
<td width="50%" valign="top">
<h3><a href="https://github.com/alissonjsb4/Jardins-de-Acacio-irrigacao-automatica">Jardins de Acácio</a></h3>
<p>Irrigação automatizada do laboratório: controle em Python, comunicação Wi-Fi por
ESP8266 e acionamento por STM32.</p>
<sub><b>Stack:</b> C · Python · ESP8266 · STM32</sub>
</td>
</tr>
</table>

## Pesquisa e desenvolvimento

**Publicações**

- Coautor — *Auto-Tuning Aging Sensor Validated Under Burn-In, Temperature and Voltage Variations*, **IEEE SBCCI 2025** (IEEE Xplore)
- Coautor — **IEEE SBCCI 2026** (aceito)
- Primeiro autor — submissão ao **IEEE BioCAS 2026**, em avaliação

**Projetos**

- **Bolsista de desenvolvimento — QHydro** (LESC/UFC, financiado por EMBRAPII/SEBRAE): firmware de estação IoT autônoma com fila store-and-forward, telemetria MQTT e atualização remota
- **Iniciação científica em confiabilidade de circuitos**, em colaboração com a IHP Microelectronics (Alemanha): automação de bancada por SCPI e pipeline de validação de dados

**Liderança**

- Fundador e presidente — **IEEE CASS, Capítulo UFC**: equipe de 10+ pessoas, workshops técnicos para 50+ estudantes, organização do 1º IEEE Latin-American Symposium on IoT
- Diretor — Clube do Hardware UFC
- **Semifinalista do Prêmio Na Prática (Fundação Estudar)** — top 100 entre 8.000+ inscritos

---

## Stack

**Linguagens** — Python · C/C++ · SQL · Java · Bash · Verilog/SystemVerilog · Assembly

**Dados e automação** — pandas · NumPy · SciPy · Playwright · ETL e junção temporal de séries · APIs REST · MQTT · object storage S3

**Infra** — Linux (systemd, deploy de serviços) · Git · agendamento de jobs

**Hardware** — FPGA (Xilinx Vivado) · STM32 · ESP32 · Raspberry Pi

---

<p align="center">
  <a href="https://www.linkedin.com/in/alissonjsb4">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white&style=for-the-badge" alt="LinkedIn">
  </a>
  <a href="mailto:alissonjsb4@gmail.com">
    <img src="https://img.shields.io/badge/e--mail-D14836?logo=gmail&logoColor=white&style=for-the-badge" alt="E-mail">
  </a>
</p>
