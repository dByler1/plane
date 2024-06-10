"use client";

import * as React from "react";

import { ISvgIcons } from "../type";

export const ModuleInProgressIcon: React.FC<ISvgIcons> = ({
  width = "20",
  height = "20",
  className,
  color = "#f39e1f",
}) => (
  <svg
    height={height}
    width={width}
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 152.93 152.95"
  >
    <g id="Layer_2" data-name="Layer 2">
      <g id="Layer_1-2" data-name="Layer 1">
        <path
          fill={color}
          d="M77.74,0C35.63-.62.78,32.9,0,74.94c-.77,42.74,33,77.34,76.23,78A76.48,76.48,0,0,0,77.74,0ZM75.46,142.68a66.24,66.24,0,1,1,3-132.45c35.71,1,66.31,31.26,64.16,70.08A66.23,66.23,0,0,1,75.46,142.68Z"
        />
        <path
          fill={color}
          d="M124.29,76.58a49.52,49.52,0,0,1-3.11,16.9c-.38,1-.77,1.27-1.81.78-2.15-1-4.34-1.92-6.56-2.72-1.3-.46-1.51-1-1-2.3a36.61,36.61,0,0,0,.64-23.77c-1-3.48-1.06-3.47,2.38-4.88,1.57-.65,3.15-1.27,4.68-2,.94-.44,1.34-.22,1.69.75A49.74,49.74,0,0,1,124.29,76.58Z"
        />
        <path
          fill={color}
          d="M94.65,32.63c-.1.22-.19.42-.27.63-1,2.5-2.08,5-3.09,7.51-.28.69-.55.89-1.37.59a37.3,37.3,0,0,0-26.82,0c-.91.34-1.15.08-1.46-.7-1-2.46-2-4.92-3.06-7.34-.42-.92-.07-1.18.69-1.46a47.66,47.66,0,0,1,34.43,0C94.06,32,94.68,32,94.65,32.63Z"
        />
        <path
          fill={color}
          d="M28.72,76.67a48.27,48.27,0,0,1,3-17.13c.45-1.25.92-1.34,2-.83,2.25,1,4.56,2,6.87,2.87.86.34,1.05.67.71,1.58a36.85,36.85,0,0,0-.07,26.36c.36,1,.3,1.46-.75,1.86-2.38.9-4.72,1.88-7,2.92-1,.43-1.33.2-1.68-.76A46.76,46.76,0,0,1,28.72,76.67Z"
        />
        <path
          fill={color}
          d="M76.37,124.22a48.11,48.11,0,0,1-16.91-3.08c-1.05-.38-1.26-.8-.79-1.82,1-2.31,2-4.66,2.93-7,.34-.87.69-1.06,1.61-.72a37.06,37.06,0,0,0,26.67,0c.75-.28,1.09-.23,1.39.55,1,2.56,2,5.13,3.18,7.65.49,1.08-.3,1.13-.86,1.34A46.53,46.53,0,0,1,76.37,124.22Z"
        />
      </g>
    </g>
  </svg>
);
