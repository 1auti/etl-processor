``` txt
src/
├── core/
│   └── abstractions/
│       ├── __init__.py
│       ├── types.py           # Type aliases, enums, dataclasses
│       ├── extractors.py      # BaseExtractor y derivadas
│       ├── parsers.py         # BaseParser
│       ├── loaders.py         # BaseLoader y derivadas
│       └── processors.py      # BaseETLProcessor y derivadas
└── etl/
    ├── extractors/            # Implementaciones concretas
    │   ├── file_extractor.py
    │   ├── s3_extractor.py
    │   └── api_extractor.py
    ├── parsers/               # Implementaciones concretas
    │   ├── apache_parser.py
    │   ├── nginx_parser.py
    │   └── json_parser.py
    ├── loaders/               # Implementaciones concretas
    │   ├── postgres_loader.py
    │   ├── csv_loader.py
    │   └── elasticsearch_loader.py
    └── processors/            # Procesadores completos
        └── log_processing_processor.py


        ```text
