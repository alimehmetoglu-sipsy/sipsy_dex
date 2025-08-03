import asyncio
import logging
from typing import Optional
from datetime import datetime
from ..schemas.command import PowerShellCommand, CommandResponse
from ..core.config import settings

logger = logging.getLogger(__name__)

class PowerShellService:
    @staticmethod
    async def execute_command(
        command: str,
        timeout: int = 30,
        working_directory: Optional[str] = None,
        run_as_admin: bool = False
    ) -> CommandResponse:
        """
        Execute a PowerShell command asynchronously
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing PowerShell command: {command}")
            
            # Check for PowerShell availability
            import shutil
            import platform
            
            # Determine PowerShell executable
            powershell_exe = None
            if platform.system() == "Windows":
                # Windows: try powershell.exe then pwsh.exe
                if shutil.which('powershell.exe'):
                    powershell_exe = 'powershell.exe'
                elif shutil.which('pwsh.exe'):
                    powershell_exe = 'pwsh.exe'
            else:
                # Linux/macOS: try pwsh (PowerShell Core)
                if shutil.which('pwsh'):
                    powershell_exe = 'pwsh'
            
            if not powershell_exe:
                # PowerShell not available
                execution_time = (datetime.now() - start_time).total_seconds()
                error_msg = "PowerShell not available on this system. Install PowerShell Core (pwsh) for cross-platform support."
                logger.warning(error_msg)
                
                return CommandResponse(
                    success=False,
                    output="",
                    error=error_msg,
                    execution_time=execution_time,
                    timestamp=start_time,
                    command=command
                )
            
            # Prepare PowerShell command
            if run_as_admin:
                # Run as administrator using Start-Process (Windows only)
                if platform.system() == "Windows":
                    ps_command = f'Start-Process {powershell_exe} -ArgumentList "-Command", "{command}" -Verb RunAs -Wait'
                else:
                    # On Linux/macOS, we can't elevate privileges the same way
                    ps_command = command
                    logger.warning("Admin privileges requested but not supported on this platform")
            else:
                ps_command = command
            
            logger.info(f"Using PowerShell executable: {powershell_exe}")
            logger.info(f"Final PowerShell command: {ps_command}")
            
            # Create process
            process = await asyncio.create_subprocess_exec(
                powershell_exe,
                '-NoProfile',
                '-NonInteractive',
                '-Command',
                ps_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory
            )
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Decode output
                output = stdout.decode('utf-8', errors='ignore').strip()
                error = stderr.decode('utf-8', errors='ignore').strip()
                
                success = process.returncode == 0
                
                logger.info(f"Command executed successfully: {command[:50]}...")
                
                return CommandResponse(
                    success=success,
                    output=output,
                    error=error if not success else None,
                    execution_time=execution_time,
                    timestamp=start_time,
                    command=command
                )
                
            except asyncio.TimeoutError:
                # Kill process if timeout
                process.kill()
                await process.wait()
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                logger.warning(f"Command timed out after {timeout}s: {command[:50]}...")
                
                return CommandResponse(
                    success=False,
                    output="",
                    error=f"Command timed out after {timeout} seconds",
                    execution_time=execution_time,
                    timestamp=start_time,
                    command=command
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Error executing command: {str(e)}")
            
            return CommandResponse(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time,
                command=command
            )
    
    @staticmethod
    async def execute_batch_commands(
        commands: list[PowerShellCommand]
    ) -> list[CommandResponse]:
        """
        Execute multiple PowerShell commands
        """
        results = []
        
        for cmd in commands:
            result = await PowerShellService.execute_command(
                command=cmd.command,
                timeout=cmd.timeout or settings.DEFAULT_TIMEOUT,
                working_directory=cmd.working_directory,
                run_as_admin=cmd.run_as_admin or False
            )
            results.append(result)
        
        return results 