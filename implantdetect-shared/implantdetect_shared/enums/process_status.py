from enum import IntEnum


class ProcessStatus(IntEnum):
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4
    CANCELED = 5

    @property
    def label(self) -> str:
        _labels = {
            ProcessStatus.PENDING: "Pendente",
            ProcessStatus.RUNNING: "Executando",
            ProcessStatus.COMPLETED: "Concluído",
            ProcessStatus.FAILED: "Falhou",
            ProcessStatus.CANCELED: "Cancelado",
        }
        return _labels[self]
