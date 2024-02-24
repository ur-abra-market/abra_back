from __future__ import annotations

from io import BytesIO
import hashlib
import pathlib
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional

from aioboto3 import Session
from types_aiobotocore_s3.service_resource import Bucket
from PIL import Image

from core.settings import aws_s3_settings
from typing_ import DictStrAny

if TYPE_CHECKING:
    from core.depends import FileObjects


class AWSS3:
    def __init__(self) -> None:
        self.session: Optional[Session] = Session(
            aws_access_key_id=aws_s3_settings.ACCESS_KEY_ID,
            aws_secret_access_key=aws_s3_settings.SECRET_ACCESS_KEY,
            region_name=aws_s3_settings.DEFAULT_REGION,
        )

    async def upload_file_to_s3(self, bucket_name: str, file: FileObjects) -> str:
        filename = file.source.filename if hasattr(file, "source") else ""
        return await self.upload(
            bucket_name=bucket_name,
            file_data={"extension": pathlib.Path(filename).suffix},
            contents=file.contents,
            file=file.source.file,
        )

    async def upload_binary_image_to_s3(
        self, bucket_name: str, byte_data: bytes, file_extension: str
    ) -> str:
        filehash = hashlib.md5(byte_data)
        filename = filehash.hexdigest()
        key = f"{filename}{file_extension}"
        async with self.session.resource("s3", region_name=aws_s3_settings.DEFAULT_REGION) as s3:
            bucket: Bucket = await s3.Bucket(bucket_name)
            await bucket.put_object(Body=byte_data, Key=key)

        return f"https://{bucket_name}.s3.amazonaws.com/{key}"

    async def uploads_list_binary_images_to_s3(
        self, bucket_name: str, images_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Uploads a list of binary images into S3.

        Args:
            bucket_name (str): Bucket name
            images_data (List[Dict[str, Any]]): List of dictionaries with data for uploading photos

        Returns:
            List[Dict[str, Any]]: List of dictionaries with data to add to the database

        Examples:
            images_data 1:
                [
                    {
                        data: [
                            {
                                "byte_data": "str",
                                "field_path": ["image_url"],
                            },
                            {
                                "byte_data": "str",
                                "field_path": ["thumbnail_url"],
                            }
                        ],
                        "variation_value_to_product_id": 50
                    },
                ]
            images_data 2:
                [
                    {
                        data: [
                            {
                                "byte_data": "str",
                                "field_path": ["image_url"],
                            },
                            {
                                "byte_data": "str",
                                "field_path": ["thumbnail_urls", "32"],
                            },
                            {
                                "byte_data": "str",
                                "field_path": ["thumbnail_urls", "128"],
                            }
                        ],
                        "order": 1
                        "product": 1
                    }
                ]
            Example return 1:
                [
                    {
                        "image_url": "str",
                        "thumbnail_url": "str",
                        "variation_value_to_product_id": 50
                    },
                ]
            Example return 2:
                [
                    {
                        "image_url": "str",
                        "thumbnail_urls": {
                            "32": "str",
                            "128": "str"
                        }
                        "order": 1
                    }
                ]

        """
        async with self.session.resource("s3", region_name=aws_s3_settings.DEFAULT_REGION) as s3:
            bucket: Bucket = await s3.Bucket(bucket_name)
            list_data = []

            for image in images_data:
                output_image = dict(image)
                output_image.pop("data")
                for data in image["data"]:
                    byte_data = data["byte_data"]
                    field_path = data["field_path"]
                    file_extension = Image.open(BytesIO(byte_data)).format.lower()
                    if file_extension == "jpeg":
                        file_extension = "jpg" 
                    name = hashlib.md5(byte_data).hexdigest()
                    key = f"{name}.{file_extension}"
                    await bucket.put_object(Body=byte_data, Key=key)
                    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"

                    temp_dir = output_image
                    for i, directory in enumerate(field_path):
                        if not temp_dir.get(directory):
                            temp_dir[directory] = {}
                        if not i == len(field_path) - 1:
                            temp_dir = temp_dir[directory]
                            continue
                        temp_dir[directory] = url
                list_data.append(output_image)
            return list_data

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
            "s3", region_name=aws_s3_settings.DEFAULT_REGION
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
            "s3", region_name=aws_s3_settings.DEFAULT_REGION
        ) as s3:
            for key in files_to_delete:
                obj = await s3.Object(bucket_name, key)
                await obj.delete()
