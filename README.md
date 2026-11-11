# Bancada de Montagem 4WD

Ambiente 3D no navegador para alunos montarem um carro robô 4WD com Arduino:
biblioteca de peças, encaixe automático, detecção de interferência e medição.

## Estrutura

| Caminho | Função |
|---|---|
| `gerar_pecas.py` | Modela cada peça em CadQuery e exporta GLB, STEP e metadados |
| `biblioteca/` | 22 peças em `.glb` (web) e `.step` (CAD), mais `catalogo.json` |
| `app.html` | Ambiente de montagem (Three.js) |
| `build.py` | Empacota `app.html` + biblioteca em `dist/index.html` (arquivo único) |
| `dist/index.html` | Versão pronta para abrir ou publicar |

## Uso

```bash
pip install cadquery
python gerar_pecas.py   # regenera a biblioteca
python build.py         # gera dist/index.html
```

Abra `dist/index.html` no navegador (precisa de internet para carregar o Three.js via CDN).

## Convenções

- Unidades em mm, eixo Z para cima.
- Cada peça declara pontos de encaixe em `catalogo.json` (`m3`, `eixo-tt`, `rasgo`, etc.).
- Submalhas com prefixo `nc_` (pinos, eixos, contatos) ficam fora do teste de interferência.
- Peças com `"aproximado": true` usam medidas típicas ou estimadas por foto; confira com paquímetro
  e ajuste em `gerar_pecas.py`. A furação das placas do chassi é a mais incerta.
