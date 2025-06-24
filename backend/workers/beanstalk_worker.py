"""Funções para interagir com o Beanstalk"""
import json
import logging
from core.semaphore import semaphore
from core.beanstalk import get_queue_connection

def consume_job():
    """
    Consome um trabalho da fila Beanstalk e processa o payload.
    """
    with get_queue_connection() as bs:
        if bs is None:
            logging.error("Erro ao conectar ao Beanstalk. Abortando o consumo de trabalho.")
            return
        while True:
            try:
                job = bs.reserve(timeout=5)
                if job is None:
                    logging.info("Nenhum trabalho encontrado. Aguardando...")
                    continue
                payload = json.loads(job.body)
                logging.info(f"Processando trabalho: {payload}")
                # Processamento vai aqui
                job.delete()
            except Exception as e:
                logging.error(f"Ocorreu um erro ao processar o trabalho: {e}")
            finally:
                semaphore.release()
                logging.info("Semáforo liberado, pronto para o próximo trabalho.")
                if 'job' in locals():
                    job.release()
                    
def add_job_to_queue(data: dict):
    """Adiciona um trabalho à fila do Beanstalk."""
    try:
        with get_queue_connection() as queue:
            json_str = json.dumps(data)
            job_data = json_str.encode('utf-8')
            job_id = queue.put(job_data)
            logging.info(f"Trabalho adicionado à fila com ID: {job_id}")
            return job_id
    except Exception as e:
        logging.exception("Erro ao adicionar trabalho à fila:")
        return None
        
def reserve_job_from_queue():
    """Reserva um trabalho da fila do Beanstalk.

    A reserva segue a ordem padrão do Beanstalkd, que é baseada em prioridade (jobs com menor valor de prioridade são reservados primeiro),
    tempo de delay e tempo de inserção. Ou seja, jobs com maior prioridade (menor valor numérico) serão reservados antes dos outros.
    """
    try:
        with get_queue_connection() as queue:
            job = queue.reserve()
            if job is None:
                logging.info("Nenhum trabalho disponível na fila.")
                return None
            logging.info(f"Trabalho reservado com ID: {job.id}")
            return job
    except Exception as e:
        logging.exception("Erro ao reservar trabalho da fila:")
        return None
        
def delete_job(job_id: int):
    """Deleta um trabalho da fila do Beanstalk."""
    try:
        with get_queue_connection() as queue:
            queue.delete(job_id)
            logging.info(f"Trabalho com ID {job_id} deletado da fila.")
            return True
    except Exception as e:
        logging.exception(f"Erro ao deletar trabalho {job_id}:")
        return False
        
def release_job(job_id: int, priority: int = 1024, delay: int = 0):
    """Libera um trabalho reservado de volta para a fila do Beanstalk."""
    try:
        with get_queue_connection() as queue:
            queue.release(job_id, priority, delay)
            logging.info(f"Trabalho com ID {job_id} liberado de volta para a fila.")
            return True
    except Exception as e:
        logging.exception(f"Erro ao liberar trabalho {job_id}:")
        return False
        
def bury_job(job_id: int, priority: int = 1024):
    """Enterra um trabalho na fila do Beanstalk, tornando-o indisponível para reserva."""
    try:
        with get_queue_connection() as queue:
            queue.bury(job_id, priority)
            logging.info(f"Trabalho com ID {job_id} enterrado na fila.")
            return True
    except Exception as e:
        logging.exception(f"Erro ao enterrar trabalho {job_id}:")
        return False
        
def get_job_stats(job_id: int):
    """Obtém as estatísticas de um trabalho na fila do Beanstalk."""
    try:
        with get_queue_connection() as queue:
            stats = queue.stats_job(job_id)
            if stats is None:
                logging.warning(f"Trabalho com ID {job_id} não encontrado na fila.")
                return None
            return stats
    except Exception as e:
        logging.exception(f"Erro ao obter estatísticas do trabalho {job_id}:")
        return None