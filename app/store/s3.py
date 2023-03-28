import hashlib
from typing import Optional, Any, Dict

from aioboto3 import Session

from core.settings import aws_s3_settings


class AWSS3:
    s3: Optional[Any] = None

    def __init__(self) -> None:
        self.session: Optional[Session] = Session()

    async def connect(self) -> None:
        self.s3 = self.session.resource(service_name="s3")

    async def disconnect(self) -> None:
        if self.s3:
            await self.s3.close()

    async def upload(
        self, file: Dict[str, Any], contents: bytes
    ) -> str:

        filehash = hashlib.md5(contents)
        filename = filehash.hexdigest()

        key = f"{filename[:2]}/{filename}{file['extension']}"
        await self.s3.upload_fileobj(
            contents, aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
        )
        return f"https://{aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET}.s3.amazonaws.com/{key}"

    async def remove(self, *files: str) -> None:
        for file in files:
            await self.s3.delete_object(aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET, file)
