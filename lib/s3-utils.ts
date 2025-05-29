import { PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from '@aws-sdk/client-s3';
import { s3Client, S3_BUCKET_NAME, S3_VIDEO_BUCKET_NAME, S3_VIDEO_BUCKET_URL } from './aws-config';

// General file upload
export async function uploadFileToS3(file: File, key: string) {
  try {
    const command = new PutObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: key,
      Body: file,
      ContentType: file.type,
      ACL: 'public-read',
    });

    await s3Client.send(command);
    return `https://${S3_BUCKET_NAME}.s3.amazonaws.com/${key}`;
  } catch (error) {
    console.error('Error uploading to S3:', error);
    throw error;
  }
}

// Video upload with specific settings
export async function uploadVideoToS3(file: File, key: string) {
  try {
    const command = new PutObjectCommand({
      Bucket: S3_VIDEO_BUCKET_NAME,
      Key: key,
      Body: file,
      ContentType: file.type,
      ACL: 'public-read',
      // Add video-specific metadata
      Metadata: {
        'x-amz-meta-video-type': 'course-video',
        'x-amz-meta-upload-date': new Date().toISOString(),
      },
    });

    await s3Client.send(command);
    return getVideoUrl(key);
  } catch (error) {
    console.error('Error uploading video to S3:', error);
    throw error;
  }
}

// Delete file from S3
export async function deleteFileFromS3(key: string) {
  try {
    const command = new DeleteObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: key,
    });

    await s3Client.send(command);
  } catch (error) {
    console.error('Error deleting from S3:', error);
    throw error;
  }
}

// Delete video from S3
export async function deleteVideoFromS3(key: string) {
  try {
    const command = new DeleteObjectCommand({
      Bucket: S3_VIDEO_BUCKET_NAME,
      Key: key,
    });

    await s3Client.send(command);
  } catch (error) {
    console.error('Error deleting video from S3:', error);
    throw error;
  }
}

// Get file URL
export function getFileUrl(key: string) {
  return `https://${S3_BUCKET_NAME}.s3.amazonaws.com/${key}`;
}

// Get video URL
export function getVideoUrl(key: string) {
  return `${S3_VIDEO_BUCKET_URL}/${key}`;
}

// Get video thumbnail URL
export function getVideoThumbnailUrl(key: string) {
  const thumbnailKey = key.replace(/\.[^/.]+$/, '-thumbnail.jpg');
  return `${S3_VIDEO_BUCKET_URL}/${thumbnailKey}`;
} 