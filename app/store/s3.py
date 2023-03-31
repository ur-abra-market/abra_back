import hashlib
from typing import Optional, Any, List, Dict


from aioboto3 import Session
from types_aiobotocore_s3.service_resource import Bucket, S3ServiceResource
from fastapi import BackgroundTasks

from core.settings import aws_s3_settings


class AWSS3:
    s3: Optional[Any] = None

    def __init__(self) -> None:
        self.session: Optional[Session] = Session(
            aws_access_key_id=aws_s3_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_s3_settings.AWS_SECRET_ACCESS_KEY,
            region_name=aws_s3_settings.AWS_DEFAULT_REGION,
        )

    async def connect(self) -> S3ServiceResource:
        ...

    async def disconnect(self):
        ...

    async def upload(
        self, bucket_name: str, file_data: Dict[str, Any], contents: bytes, file
    ) -> str:
        filehash = hashlib.md5(contents)
        filename = filehash.hexdigest()
        key = f"{filename[:2]}/{filename}{file_data['extension']}"

        # TODO: вынести в метод
        async with self.session.resource(
            "s3", region_name=aws_s3_settings.AWS_DEFAULT_REGION
        ) as s3:
            bucket: Bucket = await s3.Bucket(bucket_name)
            # TODO: в сelery или BG tasks
            await bucket.upload_fileobj(file.file, key)

        return f"https://{bucket_name}.s3.amazonaws.com/{key}"

    async def remove(
        self,
        bucket_name: str,
        files_to_delete: List[str],
    ) -> None:
        async with self.session.resource(
            "s3", region_name=aws_s3_settings.AWS_DEFAULT_REGION
        ) as s3:
            for key in files_to_delete:
                (await s3.Object(bucket_name, key)).delete()
