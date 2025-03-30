from .classes.config import Configuration
from .database import Database
from threading import Event
from time import sleep
from datetime import time, datetime
import psutil, subprocess, logging


logger = logging.getLogger('main')


def run_application(path = str, app_name = str):
    '''
    Can't comment much, got this from internet.
    Just created a way to insert variables of file and path and later convert it to bytes
    '''
    try:
        logger.info(f'Starting {app_name}')
        cmd_line = ['cmd', '/q', '/k', 'echo off']
        cmd = subprocess.Popen(cmd_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp= f'\n cd {path}\n {app_name}\n exit\n'
        batch = bytes(temp, 'utf-8')
        cmd.stdin.write(batch)
        cmd.stdin.flush()
        # result = cmd.stdout.read()
        # logger.debug(result.decode())
        logger.info('Done')
        return
    except Exception as error:
        logger.warning(f'Could not start {app_name} due {error}')
        raise error


def check_if_process_running(process_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == process_name:
            return True
    return False


def check_proctask_type(process: psutil.Process, cmdline_detail: str) -> bool:
    cmdline = process.cmdline()
    if cmdline_detail in cmdline:
        return True
    return False


def check_net_connection(process: psutil.Process) -> bool:
    '''
    Check Net Connection
    --------------------

    Test is process has net connection stablished
    '''
    try:
        net_connection = process.net_connections()[0]
        if net_connection.status == 'ESTABLISHED':
            return True
    except Exception as error:
        logger.warning(f'Could not get net connection due {error}')
        return False


def start_restart_proctask(process_path: str, process_name: str, cmdline_detail: str) -> bool:
    try:
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name and check_proctask_type(process, cmdline_detail):
                if check_net_connection(process):
                    return
                else:
                    logger.info(f'No connectio, killing {process_name}')
                    process.kill()
                    sleep(5)
        run_application(process_path, f'{process_name} {cmdline_detail}')
        return
    except Exception as error:
        logger.error(f'Could not start/restart {process_name} due {error}')
        raise error


def check_operation_time(start_print_time: time, end_print_time: time) -> bool:
    '''
    Check active operation time
    '''
    now = datetime.now().time()
    if now >= start_print_time and now <= end_print_time:
        return True
    return False


def sleep_routine(sleep_time: int, event: Event) -> bool:
    for _ in range(sleep_time):
        if event.is_set():
            return True
        sleep(1)
    return False


def proctask_routine(config: Configuration, event: Event) -> None:
    while True:
        if event.is_set():
            logger.info('Terminating routine')
            return
        if check_operation_time(config.operation_start_time, config.operation_end_time):
            for process in config.process_list:
                try:
                    start_restart_proctask(process.process_path, process.process_name, process.cmdline_detail)
                    sleep(config.sleep_interval)
                except Exception as error:
                    logger.warning(f'Error {error}')
            logger.info(f'Waiting...')
            if sleep_routine(config.sleep_time, event):
                logger.info('Terminating routine')
                return
        else:
            logger.info(f'Out of operation time...')
            if sleep_routine(config.sleep_time, event):
                logger.info('Terminating routine')
                return                


def proctask_monitor(database: Database, event: Event, start_delay: int=3) -> None:
    '''
    Start main function
    '''
    logger.info('Proctask Monitor Starting')
    if event.is_set():
        return
    try:
        config = database.get('config')
    except Exception as error:
        logger.critical(f'Could not load config file due {error}')
        event.set()
        return

    if start_delay:
        logger.info(f'Initialization delay {start_delay} seconds.')
        for _ in range(start_delay):
            if event.is_set():
                return
            sleep(1)
    proctask_routine(config, event)