import argparse
import sys

from youtubebot.config import load_settings
from youtubebot.registry import VIDEO_TYPES


def main():
    parser = argparse.ArgumentParser(description="Generate upload-ready MP4 videos.")
    parser.add_argument("video_type", choices=sorted(VIDEO_TYPES))
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Number of videos to create.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload each completed video to YouTube.",
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("count must be at least 1")

    try:
        settings = load_settings()
        video_maker = VIDEO_TYPES[args.video_type](settings)
        uploader = None

        if args.upload:
            from youtubebot.youtube_upload import YouTubeUploader

            uploader = YouTubeUploader(settings.project_root)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)

    created = 0
    uploaded = 0
    upload_failed = 0

    for number in range(1, args.count + 1):
        print(f"\nCreating video {number} of {args.count}...")

        try:
            result = video_maker.create()
        except Exception as error:
            print(f"Video {number} failed: {error}", file=sys.stderr)
            continue

        created += 1
        print(f"Created:  {result.output_path}")
        print(f"Source:   {result.source_url}")
        print(f"Metadata: {result.metadata_path}")

        if uploader:
            print("Uploading to YouTube...")

            try:
                upload_result = uploader.upload(
                    result.output_path,
                    result.metadata_path,
                )
            except Exception as error:
                upload_failed += 1
                print(f"Upload failed: {error}", file=sys.stderr)
                continue

            uploaded += 1
            print(f"Uploaded: {upload_result['youtube_url']}")

    if args.upload:
        print(
            f"\nFinished: {created} of {args.count} videos created, "
            f"{uploaded} uploaded, {upload_failed} upload failures."
        )
    else:
        print(f"\nFinished: {created} of {args.count} videos created.")

    if created != args.count or upload_failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
