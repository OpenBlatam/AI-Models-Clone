import {
    Grid3X3,
    Droplets,
    Snowflake,
    Zap,
    Microscope,
    Flame,
    LayoutDashboard,
    LucideIcon,
    LucideProps
} from 'lucide-react';

const ICON_MAP: Record<string, LucideIcon> = {
    Grid3X3,
    Droplets,
    Snowflake,
    Zap,
    Microscope,
    Flame,
    LayoutDashboard,
};

interface ModuleIconProps extends LucideProps {
    name: string;
}

export function ModuleIcon({ name, ...props }: ModuleIconProps) {
    const Icon = ICON_MAP[name] || Grid3X3;
    return <Icon {...props} />;
}
