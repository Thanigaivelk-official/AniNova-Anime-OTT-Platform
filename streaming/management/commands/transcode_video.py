from django.core.management.base import BaseCommand
from streaming.transcoder import transcode_to_hls


class Command(BaseCommand):
    help = 'Transcodes raw uploaded video into HLS .m3u8 adaptive bitrate chunks'

    def add_arguments(self, parser):
        parser.add_argument('asset_id', type=int, help='ID of the VideoAsset to transcode')

    def handle(self, *args, **options):
        asset_id = options['asset_id']
        self.stdout.write(f"Initiating HLS transcode for VideoAsset #{asset_id}...")
        success, message = transcode_to_hls(asset_id)
        if success:
            self.stdout.write(self.style.SUCCESS(f"Success: {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {message}"))
