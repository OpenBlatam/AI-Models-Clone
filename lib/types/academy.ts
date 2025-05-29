export interface Academy {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  instructor: string;
  category: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  totalClasses: number;
  totalDuration: string;
  experience: number;
  s3Config: {
    bucketName: string;
    clientKey: string;
    region: string;
  };
  classes?: AcademyClass[];
  createdAt: string;
  updatedAt: string;
}

export interface AcademyClass {
  id: string;
  academyId: string;
  title: string;
  description: string;
  videoUrl: string;
  thumbnail: string;
  duration: string;
  order: number;
  isCompleted: boolean;
  progress: number;
  experience: number;
  resources?: Resource[];
  createdAt: string;
  updatedAt: string;
}

export interface Resource {
  id: string;
  type: 'pdf' | 'link' | 'code';
  title: string;
  url: string;
}

export interface AcademyProgress {
  id: string;
  userId: string;
  academyId: string;
  currentClassId: string;
  completedClasses: string[];
  totalProgress: number;
  lastAccessed: string;
  createdAt: string;
  updatedAt: string;
} 