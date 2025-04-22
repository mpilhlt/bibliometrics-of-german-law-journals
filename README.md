# Measuring Bibliometric Coverage of German Law Journals

This repo contains code and data for the paper "Measuring Bibliometric Coverage of German Law Journals" by Boulanger/Fejzo/Rimmert. See the [current HTML version of the paper](https://cboul.pages.mpcdf.de/kb-bibliometry/paper.html) for more details.

The Web of Science (WoS), Scopus and OpenAlex data used in this article were provided by the German Competence Network for Bibliometrics funded by the Federal Ministry of Education and Research (Grant: 16WIK2101A). We thank the publishers Mohr Siebeck, Duncker & Humblot and Nomos for providing us with the metadata on journal articles used in section 4.

While the original WoS and Scopus data are subject to legal restrictions that prevent us from sharing them, we have made a derived version of the data available in the `data/kb_data` folder for reproducibility purposes. The notebooks that were used to generate this data are in the `notebooks` folder. As far as these notebooks notebooks require access to the databases of the German Competence Network for Bibliometrics, they will only work if you have the necessary access credentials and the appropriate VPN connection, dependent on institutional membership in the network.

Some code has been written with the help of LLM coding assistance.

## Usage

The easiest way to run the code is using [`uv`](https://docs.astral.sh/uv) in order to create the runtime enviroment.

```
uv sync
```

and then use an IDE such as Visual Studio Code which can view and run Jupyter notebooks.

Alternatively, use a containerized Jupyter server such as the following:

```
docker pull jupyter/base-notebook
docker run -p 8888:8888 -v <path_to_your_work_dir>:/home/jovyan/work jupyter/base-notebook
```

