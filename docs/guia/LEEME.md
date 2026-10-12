# Guía de uso

`guia_uso.md` es la fuente de `TECLA_GUIA_USO.pdf`. Para regenerarla, desde la raíz del repositorio:

```bash
pandoc docs/guia/guia_uso.md -o TECLA_GUIA_USO.pdf --pdf-engine=xelatex --resource-path=. \
       -V mainfont="Helvetica Neue" -V monofont="Menlo" -V monofontoptions="Scale=0.85"
```

Las capturas son las de `web/img/`.
