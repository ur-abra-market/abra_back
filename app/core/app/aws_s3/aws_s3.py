from __future__ import annotations

import hashlib
import pathlib
from typing import TYPE_CHECKING, BinaryIO, List, Optional

from aioboto3 import Session
from types_aiobotocore_s3.service_resource import Bucket

from core.settings import aws_s3_settings
from typing_ import DictStrAny

if TYPE_CHECKING:
    from core.depends import FileObjects


class AWSS3:
    def __init__(self) -> None:
        self.session: Optional[Session] = Session(
            aws_access_key_id=aws_s3_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_s3_settings.AWS_SECRET_ACCESS_KEY,
            region_name=aws_s3_settings.AWS_DEFAULT_REGION,
        )

    async def upload_file_to_s3(self, bucket_name: str, file: FileObjects) -> str:
        filename = file.source.filename or ""
        return await self.upload(
            bucket_name=bucket_name,
            file_data={"extension": pathlib.Path(filename).suffix},
            contents=file.contents,
            file=file.source.file,
        )

    async def delete_file_from_s3(self, bucket_name: str, url: str) -> None:
        key_to_delete = ["/".join(url.split("/")[-2:])]
        await self.remove(
            bucket_name=bucket_name,
            files_to_delete=key_to_delete,
        )

    async def upload(
        self, bucket_name: str, file_data: DictStrAny, contents: bytes, file: BinaryIO
    ) -> str:
        filehash = hashlib.md5(contents)
        filename = filehash.hexdigest()
        key = f"{filename}{file_data['extension']}"
        async with self.session.resource(  # type: ignore[union-attr]
            "s3", region_name=aws_s3_settings.AWS_DEFAULT_REGION
        ) as s3:
            bucket: Bucket = await s3.Bucket(bucket_name)
            await bucket.upload_fileobj(file, key)

        return f"https://{bucket_name}.s3.amazonaws.com/{key}"

    async def remove(
        self,
        bucket_name: str,
        files_to_delete: List[str],
    ) -> None:
        async with self.session.resource(  # type: ignore[union-attr]
            "s3", region_name=aws_s3_settings.AWS_DEFAULT_REGION
        ) as s3:
            for key in files_to_delete:
                obj = await s3.Object(bucket_name, key)
                await obj.delete()
