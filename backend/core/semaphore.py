from threading import Semaphore

"""
Limitação de concorrência usando semáforo.

O semáforo é usado para controlar o acesso a um recurso compartilhado,
permitindo que apenas um thread acesse o recurso por vez.

Este semáforo será utilizado para garantir que somente uma operação
seja feita no modelo de treinamento por vez, evitando condições de
corrida e garantindo a integridade dos dados.
"""

semaphore = Semaphore(1)