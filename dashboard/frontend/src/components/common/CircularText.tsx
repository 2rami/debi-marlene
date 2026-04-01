import React, { useEffect } from 'react';
import { motion, useAnimation, useMotionValue } from 'framer-motion';

interface CircularTextProps {
  text: string;
  spinDuration?: number;
  onHover?: 'slowDown' | 'speedUp' | 'pause' | 'goBonkers';
  className?: string;
}

const getRotationTransition = (duration: number, from: number, loop: boolean = true) => ({
  from,
  to: from + 360,
  ease: 'linear' as const,
  duration,
  type: 'tween' as const,
  repeat: loop ? Infinity : 0
});

const getTransition = (duration: number, from: number) => ({
  rotate: getRotationTransition(duration, from),
  scale: { type: 'spring' as const, damping: 20, stiffness: 300 }
});

const CircularText: React.FC<CircularTextProps> = ({
  text,
  spinDuration = 20,
  onHover = 'speedUp',
  className = ''
}) => {
  const letters = Array.from(text);
  const controls = useAnimation();
  const rotation = useMotionValue(0);

  useEffect(() => {
    const start = rotation.get();
    controls.start({
      rotate: start + 360,
      scale: 1,
      transition: getTransition(spinDuration, start)
    });
  }, [spinDuration, text, onHover, controls]);

  const handleHoverStart = () => {
    const start = rotation.get();
    if (!onHover) return;

    switch (onHover) {
      case 'slowDown':
        controls.start({ rotate: start + 360, scale: 1, transition: getTransition(spinDuration * 2, start) });
        break;
      case 'speedUp':
        controls.start({ rotate: start + 360, scale: 1, transition: getTransition(spinDuration / 4, start) });
        break;
      case 'pause':
        controls.start({ rotate: start, scale: 1, transition: { rotate: { type: 'spring', damping: 20, stiffness: 300 }, scale: { type: 'spring', damping: 20, stiffness: 300 } } });
        break;
      case 'goBonkers':
        controls.start({ rotate: start + 360, scale: 0.8, transition: getTransition(spinDuration / 20, start) });
        break;
    }
  };

  const handleHoverEnd = () => {
    const start = rotation.get();
    controls.start({ rotate: start + 360, scale: 1, transition: getTransition(spinDuration, start) });
  };

  return (
    <motion.div
      className={`m-0 mx-auto rounded-full relative font-black text-center cursor-pointer origin-center ${className}`}
      style={{ rotate: rotation }}
      initial={{ rotate: 0 }}
      animate={controls}
      onMouseEnter={handleHoverStart}
      onMouseLeave={handleHoverEnd}
    >
      {letters.map((letter, i) => {
        const rotationDeg = (360 / letters.length) * i;
        const factor = Math.PI / letters.length;
        const x = factor * i;
        const y = factor * i;
        const transform = `rotateZ(${rotationDeg}deg) translate3d(${x}px, ${y}px, 0)`;
        return (
          <span
            key={i}
            className="absolute inline-block inset-0 text-[11px] transition-all duration-500 ease-[cubic-bezier(0,0,0,1)]"
            style={{ transform, WebkitTransform: transform }}
          >
            {letter}
          </span>
        );
      })}
    </motion.div>
  );
};

export default CircularText;
