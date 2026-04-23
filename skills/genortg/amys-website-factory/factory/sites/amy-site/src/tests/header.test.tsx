import { render, screen } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, className }: any) => (
    <a href={href} className={className}>{children}</a>
  ),
}));

import { SiteHeader } from '../components/SiteHeader';

test('renders SiteHeader with brand, CTA and nav', () => {
  render(<SiteHeader />);
  expect(screen.getByText(/AMY/)).toBeTruthy();
  expect(screen.getByText(/Start a project/)).toBeTruthy();
  expect(screen.getByLabelText('Main navigation')).toBeTruthy();
});
