import { Footer as FT } from 'flowbite-react';

export default function Footer() {
  return (
    <FT container={true} className='mx-auto'>
      <FT.Copyright href="https://www.vt.edu/" by="Virginia Tech" year={2023} />
      <FT.LinkGroup>
        <FT.Link href="#">About</FT.Link>
        <FT.Link href="#">Privacy Policy</FT.Link>
        <FT.Link href="#">Licensing</FT.Link>
        <FT.Link href="#">Contact</FT.Link>
      </FT.LinkGroup>
    </FT>
  );
}
