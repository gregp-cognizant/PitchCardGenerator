import uuid
import subprocess
import os
import asyncio
import logging


class PPTXToPDFConverter:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    async def convert(self, source_path: str, output_file: str) -> (bool, str):
        user_profile_path = self._create_user_profile_path()
        output_path, output_file_name = self._prepare_output_paths(output_file)
        return await self._attempt_conversion(
            source_path, output_path, output_file_name, user_profile_path
        )

    def _create_user_profile_path(self) -> str:
        return f"/tmp/libreoffice_user_{uuid.uuid4()}"

    def _prepare_output_paths(self, output_file: str) -> (str, str):
        output_path = os.path.dirname(output_file) + "/converted_from_pptx"
        output_file_name = os.path.basename(output_file)
        return output_path, output_file_name

    async def _attempt_conversion(
        self,
        source_path: str,
        output_path: str,
        output_file_name: str,
        user_profile_path: str,
    ) -> (bool, str):
        attempts = 0
        output_full_path = os.path.join(
            output_path, output_file_name.replace(".pptx", ".pdf")
        )

        while attempts < self.max_retries:
            try:
                await self._execute_conversion(
                    source_path, output_path, user_profile_path
                )

                # Verify output file's existence and integrity
                if (
                    os.path.exists(output_full_path)
                    and os.path.getsize(output_full_path) > 0
                ):
                    return True, output_full_path
                else:
                    self.logger.error(
                        f"Conversion completed but output file is missing or empty: {output_full_path}"
                    )
                    attempts += 1
            except subprocess.CalledProcessError as e:
                self.logger.error(
                    f"LibreOffice conversion failed with CalledProcessError: {e}"
                )
                attempts += 1
            except Exception as e:
                self.logger.error(f"Unexpected error during conversion: {e}")
                attempts += 1

        self.logger.error(
            f"Conversion failed after {self.max_retries} attempts: Source: {source_path}, Output: {output_full_path}"
        )
        return False, output_full_path

    def _prepare_environment_and_output_file(
        self, output_full_path: str, user_profile_path: str
    ):
        env = os.environ.copy()
        env["UserInstallation"] = f"file://{user_profile_path}"

        if os.path.exists(output_full_path):
            os.remove(output_full_path)
            self.logger.info(
                f"Deleted existing file before re-conversion: {output_full_path}"
            )

    async def _execute_conversion(
        self, source_path: str, output_path: str, user_profile_path: str
    ):
        # Set the user profile path in the environment variable
        env = os.environ.copy()
        env["UserInstallation"] = f"file://{user_profile_path}"

        self.logger.info(f"Attempting to convert file: {source_path} to {output_path}")

        process = await asyncio.create_subprocess_exec(
            "libreoffice",
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            source_path,
            "--outdir",
            output_path,
            env=env,  # Use the modified environment
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            self.logger.error(
                f"LibreOffice conversion failed, Return Code: {process.returncode}, Stdout: {stdout.decode()}, Stderr: {stderr.decode()}"
            )
            raise subprocess.CalledProcessError(
                process.returncode, "libreoffice", output=stdout.decode()
            )

        self.logger.info(
            f"LibreOffice conversion command executed, Stdout: {stdout.decode()}, Stderr: {stderr.decode()}"
        )
