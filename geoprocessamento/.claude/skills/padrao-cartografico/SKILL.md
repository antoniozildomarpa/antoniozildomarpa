---
name: padrao-cartografico
description: Padrão de qualidade para todo mapa, carta imagem e figura de mapa dos casos técnicos - objetivo antes de começar, título alinhado ao objetivo, cores suaves, pouca informação por mapa, elementos técnicos completos e conferência final do objetivo. Use antes de produzir qualquer mapa ou figura e na revisão de cada um.
---

# Padrão cartográfico

Os mapas são assinados por técnico habilitado e lidos por quem não é especialista: advogados, chefias, procuradores, pareceristas. Por isso, precisam ter qualidade técnica de excelência e, ao mesmo tempo, ser entendidos à primeira vista.

## 1. Antes de começar: o objetivo

Nenhum mapa começa sem esta definição, escrita em uma frase:

> **Este mapa mostra que...** (ex.: "a área embargada fica inteiramente dentro do imóvel"; "houve supressão da vegetação entre agosto de 2025 e abril de 2026"; "o imóvel sobrepõe a Terra Indígena X em 12,4 ha").

A partir do objetivo, decida:
- **qual é a informação principal**, que precisa aparecer em primeiro plano;
- **quais camadas são indispensáveis** para entender essa informação, e só essas;
- **qual o enquadramento** que deixa a informação principal grande e central;
- **o título**, que diz o objetivo em linguagem simples.

Registre o objetivo no `--objetivo` da figura e na ficha do caso.

## 2. Pouca informação por mapa

- Cada mapa responde a **uma** pergunta.
- Se há muitas informações, faça **uma sequência de mapas**, cada um com poucas camadas. Exemplos de sequência: localização geral → imóvel e área embargada → evolução da vegetação (um mapa por data) → sobreposições com áreas protegidas.
- Prefira de 3 a 5 itens na legenda. Mais que 6 é sinal de que o mapa deve ser dividido.
- Rótulos só onde ajudam a leitura (vértices citados no texto, nome do imóvel). Nada de rótulo decorativo.

## 3. Cores suaves e hierarquia visual

- Use a paleta padrão de `geoprocessamento/automacao-sei/scripts/estilos.py`, por papel da camada: `foco`, `imovel`, `hidrografia`, `uc`, `ti`, `app`, `desmatamento`, `referencia`, `vertices`.
- **Só a informação principal recebe cor forte** (papel `foco`). O resto fica em tons suaves, contornos finos ou tracejados.
- Preenchimentos sempre semitransparentes sobre imagem, para não esconder o terreno.
- Evite vermelho e verde puros lado a lado (daltonismo) e nunca use mais de uma cor forte.
- Fundo de imagem em cor real, no estilo natural já validado (skill `landsat-estilo-natural-tiarg`).

## 4. Elementos técnicos

### Mapas e cartas imagem completos (anexos)

Seguem os modelos de layout já produzidos pelo usuário (cabeçalho, quadro de dados técnicos, mapa de localização) e a skill `producao-carta-imagem`. Todo mapa completo tem:

| Elemento | Observação |
| --- | --- |
| Título | Alinhado ao objetivo, em linguagem simples |
| Mapa principal | Informação principal grande e central |
| Legenda | Só o que aparece no mapa, com nomes legíveis (nunca nome de arquivo) |
| Escala gráfica e escala numérica | A numérica vale para o tamanho de impressão do layout |
| Indicação do norte | |
| Sistema de referência | Datum SIRGAS 2000; projeção e zona (ou "coordenadas geográficas") |
| Grade de coordenadas | Com valores nas bordas, em graus-minutos-segundos ou UTM |
| Mapa de localização | Estado e município, com o destaque da área |
| Fontes dos dados | Cada camada com origem e data (inclusive data e hora das consultas ao SISCOM e à SEMAS-PA) |
| Imagem | Sensor, data da imagem e resolução |
| Data de elaboração | |
| Responsável técnico | Nome, formação e registro profissional |
| Órgão e identificação | Logotipo, número do processo e número do mapa |

As normas técnicas aplicáveis (ABNT e convenções cartográficas do IBGE) são a referência. Quando houver dúvida sobre um item normativo, confirme na norma antes de afirmar no documento.

### Figuras no corpo do texto

Mostram só a área útil (skill `figura-mapa-legenda`). Sem cabeçalho e sem quadro de dados técnicos, mas sempre com **legenda sobreposta, escala gráfica e norte**, e uma legenda de figura no documento que informe:
- o que a figura mostra, alinhado ao objetivo;
- a imagem de fundo (sensor e data);
- o sistema de referência, quando relevante.

Exemplo: "Figura 2 – Área embargada (78,63 ha) no interior do imóvel, sobre imagem PlanetScope de 10/05/2026. SIRGAS 2000."

## 5. Conferência final (obrigatória)

Com o mapa ou a figura na versão considerada final, olhe a imagem e responda por escrito:

1. **O objetivo foi atendido por este mapa?**
2. **Quem olhar vê, em primeiro plano, a informação principal do objetivo?**
3. **O título (ou a legenda da figura) está alinhado ao objetivo?**
4. **Há informação demais?** Se sim, dividir em uma sequência de mapas.
5. **Um leitor que não é especialista entende o mapa sem explicação?**
6. **Todos os elementos técnicos estão presentes** (seção 4)?

Se alguma resposta for "não", corrija e confira de novo. Só depois marque a figura como conferida e mostre ao usuário, com as respostas.
