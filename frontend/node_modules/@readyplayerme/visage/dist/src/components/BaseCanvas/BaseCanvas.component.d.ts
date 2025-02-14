import { ReactNode, FC, CSSProperties } from 'react';
import { Dpr } from '@react-three/fiber';
import { CameraProps } from 'src/types';
interface BaseCanvasProps extends CameraProps {
    children?: ReactNode;
    fov?: number;
    style?: CSSProperties;
    dpr?: Dpr;
    className?: string;
}
export declare const BaseCanvas: FC<BaseCanvasProps>;
export {};
