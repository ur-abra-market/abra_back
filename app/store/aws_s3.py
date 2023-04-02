import hashlib
import pathlib
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from aioboto3 import Session
from types_aiobotocore_s3.service_resource import Bucket, S3ServiceResource

from core.settings import aws_s3_settings

if TYPE_CHECKING:
    from core.depends import FileObjects


class AWSS3:
    s3: Optional[Any] = None

    def __init__(self) -> None:
        self.session: Optional[Session] = Session(
            aws_access_key_id=aws_s3_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_s3_settings.AWS_SECRET_ACCESS_KEY,
            region_name=aws_s3_settings.AWS_DEFAULT_REGION,
        )

    async def upload_file_to_s3(self, bucket_name: str, file: "FileObjects") -> str:
        return await self.upload(
            bucket_name=bucket_name,
            file_data={"extension": pathlib.Path(file.source.filename).suffix},
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
        self, bucket_name: str, file_data: Dict[str, Any], contents: bytes, file: BytesIO
    ) -> str:
        filehash = hashlib.md5(contents)
        filename = filehash.hexdigest()
        key = f"{filename[:2]}/{filename}{file_data['extension']}"

        async with self.session.resource(
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
        async with self.session.resource(
            "s3", region_name=aws_s3_settings.AWS_DEFAULT_REGION
        ) as s3:  # type: S3ServiceResource
            for key in files_to_delete:
                obj = await s3.Object(bucket_name, key)
                await obj.delete()
