from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile

from storages.backends.s3boto3 import S3Boto3Storage

class OptimizationStorage(S3Boto3Storage):

    def _save(self, name, content):
        original_size = content.size
        print(f"Размер файла до оптимизации: {original_size / 1024:.2f} KB")

        try:
            image = Image.open(content)
            output = BytesIO()

            image.save(output, format='WebP', quality=80)

            output.seek(0)
            content = ContentFile(output.read(), name)

            optimized_size = content.size
            print(f"Размер файла после оптимизации: {optimized_size / 1024:.2f} KB")

        except IOError:
            return super()._save(name, content)

        return super()._save(name, content)
