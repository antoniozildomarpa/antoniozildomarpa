---
name: figura-mapa-legenda
description: Gera a figura de mapa para o corpo de relatórios, pareceres, informações e manifestações técnicas - só a área útil, sem cabeçalho e sem dados técnicos, com legenda sobreposta no canto que não cobre a área de interesse, escala e norte. Use quando o texto mencionar um mapa que precisa aparecer como figura.
---

# Figura de mapa com legenda

Leia antes a skill `padrao-cartografico`: o objetivo da figura vem primeiro.

## 1. Planejar a figura

Para cada mapa citado no texto, defina:
- **objetivo**, em uma frase ("Mostrar que a área embargada fica dentro do imóvel");
- **camadas indispensáveis**, de cima para baixo (a imagem de fundo por último);
- **foco**: as camadas que definem o enquadramento (normalmente o imóvel ou a área principal);
- **papel de cada camada** na paleta: `foco`, `imovel`, `hidrografia`, `uc`, `ti`, `app`, `desmatamento`, `referencia`, `vertices`;
- **nome legível** de cada camada na legenda, com a área quando ajudar ("Área embargada (78,63 ha)");
- **número da figura**, na ordem em que aparece no texto.

Se a figura precisar de mais de 5 camadas na legenda, divida em duas ou mais figuras.

## 2. Gerar

Com o Python do QGIS (ver skill `projeto-qgis-caso`):

```
"<python-qgis.bat>" geoprocessamento/automacao-sei/scripts/figura_mapa.py --pasta "<pasta do caso>" \
  --numero 1 --nome-curto area_embargada \
  --objetivo "Mostrar a localização da área embargada no interior do imóvel" \
  --legenda-figura "Área embargada no interior do imóvel, sobre imagem PlanetScope de 10/05/2026" \
  --camadas vertices_area_embargada poligono_area_embargada imovel_car hidrografia imagem_planet \
  --foco imovel_car --principal poligono_area_embargada \
  --estilos "imovel_car=imovel" "hidrografia=hidrografia:nome" \
  --nomes "vertices_area_embargada=Vértices" "poligono_area_embargada=Área embargada (78,63 ha)" "imovel_car=Imóvel (CAR)" "hidrografia=Rio"
```

Opções úteis:
- `--principal`: camadas da informação principal, que os rótulos não podem cobrir (padrão: as do foco);
- `--margem 0.35`: folga em volta do foco (aumente se a legenda cobrir a área);
- `--largura-mm 160 --altura-mm 110`: tamanho na página (160 mm cabe na largura útil de uma folha A4);
- `--estilos "camada=papel:campo"`: aplica a paleta e rotula pelo campo indicado;
- `--sem-legenda`, `--sem-escala`, `--sem-norte`: só com motivo;
- `--nao-salvar-layout`: não guarda o layout no projeto.

O que o script faz sozinho:
- desenha em SIRGAS 2000 / UTM da zona do foco, para formas e escala corretas;
- escolhe o canto da legenda com menor sobreposição com a área de foco; escala e norte vão para os cantos que sobrarem;
- legenda com fundo branco semitransparente, sem a imagem de fundo (ela vai na legenda da figura);
- escala gráfica refinada (barra de 1 mm, contorno de 0,15 mm), em m ou km, números no padrão brasileiro e texto colado à barra;
- grade de coordenadas só com traços curtos na borda e valores em GMS (S/O), com intervalo escolhido pela escala (3 a 5 divisões); `--sem-grade` para retirar;
- revisão de brilho e contraste de toda imagem de satélite, com ajuste automático (realce 2%–98%, gama e saturação) e registro de antes e depois no JSON; `--ajuste-imagem so-medir` só aponta o problema;
- linhas finas e rótulos com buffer branco, sempre exibidos, fora da informação principal (paleta de `estilos.py`);
- revisão automática dos rótulos: quantos foram exibidos, quais ficaram sem espaço, cortados na borda ou sobre a informação principal (campo `rotulos` e `alertas` do JSON);
- exporta `04_Figuras/Figura_NN_<nome>.png` a 300 dpi e o `.json` com objetivo, escala, cantos e as perguntas de conferência;
- guarda o layout no projeto (`Figura_NN`) para ajuste fino no QGIS, com cópia de segurança do projeto;
- registra a figura na ficha e no registro do caso.

## 3. Conferir (obrigatório)

1. Abra o PNG e olhe a figura inteira.
2. Responda às perguntas do campo `conferencia` do JSON (as mesmas da skill `padrao-cartografico`).
3. Se o JSON trouxer `alertas` (legenda sobre a área de foco, rótulo sem espaço, cortado ou sobre a informação principal), corrija: aumente `--margem`, tire rótulos dispensáveis ou divida a figura, e gere de novo.
4. Corrija o que for preciso e gere de novo, com o mesmo número.
5. Quando todas as respostas forem "sim", mude `"conferido": true` no JSON da figura e na lista `figuras` de `ficha.json`, e mostre a figura ao usuário com as respostas.

## 4. No documento

A figura entra logo após o parágrafo que a menciona, com a legenda do campo `legenda_figura`, completada com o sistema de referência quando relevante. O texto deve citar a figura pelo número ("conforme a Figura 1").
