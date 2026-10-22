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

## 3a. Linhas finas

- Contornos e linhas **o mais finos possível**, no limite em que ainda se enxergam sobre a imagem. Nada de traço grosseiro.
- Referência a 300 dpi: 0,2 a 0,3 mm para contornos de contexto; até 0,35 a 0,4 mm só para a informação principal.
- Moldura do mapa e da legenda: 0,2 a 0,25 mm, em cinza.
- Se uma linha fina some sobre a imagem, troque a cor por uma mais contrastante, em vez de engrossar.

## 3a-2. Grade de coordenadas e escala gráfica

- **Grade só com traço curto junto à borda**, indicando a posição da coordenada; nenhuma linha atravessando o mapa. Valores na borda, em graus-minutos-segundos (S/O), pequenos.
- **Intervalo da grade ajustado à escala**: cerca de 3 a 5 divisões na largura do mapa, com valores "redondos" (1″, 5″, 10″, 30″, 1′, 2′, 5′, 10′, 30′, 1°...). Nem grade apertada, nem mapa quase sem grade.
- **Escala gráfica refinada**: barra baixa (cerca de 1 mm), contorno fino (0,15 mm), poucas divisões, números no padrão brasileiro e **texto colado à barra**, sem espaço sobrando.
- Legenda, escala e norte discretos, em proporção com o mapa: o destaque é sempre a informação principal.

## 3b. Rótulos

- **Sempre com buffer (halo) branco**, para serem lidos sobre a imagem.
- **Sempre visíveis**: nenhum rótulo importante pode sumir por falta de espaço.
- **Nunca atrapalham a informação principal**: ficam fora do polígono principal, ao lado dos pontos, acompanhando as linhas. O interior do polígono de foco funciona como obstáculo para os rótulos.
- Texto pequeno e sóbrio (6 a 7 pt, cinza-escuro). Rotule só o que o texto do documento cita ou o que o leitor precisa para entender.
- **Revisão de rótulos é obrigatória em todo mapa**: confira se algum ficou sem espaço, cortado na borda, sobre a informação principal ou sobreposto a outro. O script da figura faz essa conferência automaticamente e lista os problemas em `alertas`; mesmo sem alertas, olhe a imagem.

## 3c. Imagens de satélite: brilho e contraste

Toda imagem de fundo passa por **revisão de ajuste** antes de o mapa ser considerado pronto:
- não pode ficar escura, com pouco brilho e luz, nem apagada (pouco contraste), nem estourada;
- as cores continuam naturais e suaves: o realce não pode deixar a vegetação com verde artificial.

O script `revisao_imagem.py` faz isso sozinho em toda figura (e pode ser usado direto num recorte GeoTIFF):
1. mede brilho, contraste, pixels quase pretos, pixels estourados e saturação, na área exata do mapa;
2. se houver problema, aplica realce linear pelos percentis de 2% e 98% calculados dos próprios pixels da área (os mesmos limites nas três bandas, para não mudar o equilíbrio de cores), ajusta a gama até o brilho de referência e reduz a saturação se o verde ficar forte demais;
3. confere de novo e registra antes, ajuste e depois no JSON da figura.

Referências: brilho médio entre 105 e 150 (escala de 0 a 255), contraste (desvio) acima de 18, até 10% de pixels quase pretos, até 3% estourados, saturação média até 0,40. Mesmo com o ajuste automático, **olhe a imagem**: área com nuvem, sombra ou queimada pode pedir ajuste manual.

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
6. **Todos os rótulos estão visíveis, com buffer, sem cobrir a informação principal?**
7. **As linhas estão finas, sem traço grosseiro, e ainda visíveis sobre a imagem?**
8. **A imagem de satélite está com brilho e contraste adequados, cores naturais, sem ficar escura?**
9. **A grade tem só traços na borda, com intervalo adequado à escala? A escala gráfica está refinada, com o texto junto à barra?**
10. **Todos os elementos técnicos estão presentes** (seção 4)?

Se alguma resposta for "não", corrija e confira de novo. Só depois marque a figura como conferida e mostre ao usuário, com as respostas.
