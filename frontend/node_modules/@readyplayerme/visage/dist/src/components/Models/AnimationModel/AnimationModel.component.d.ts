import { FC } from 'react';
import { BaseModelProps } from 'src/types';
export interface AnimationModelProps extends BaseModelProps {
    modelSrc: string | Blob;
    animationSrc: string | Blob;
    rotation?: number;
    scale?: number;
    idleRotation?: boolean;
    headMovement?: boolean;
}
export declare const AnimationModel: FC<AnimationModelProps>;
