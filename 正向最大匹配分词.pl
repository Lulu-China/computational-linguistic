open(Dic,"word.txt")||die("can not open the lexicon!\n");
print "Loading  dictionary...\n";
$MaxLen=0;
while(<Dic>){
	chomp;
	$mapDic{$_}="A";
	if ( length > $MaxLen){
		$MaxLen=length; 
	}
}
close(Dic);
print "Done Loading\n";

while(1){
	print "Pls Input Sentence for segment(Press \"q\" to exit ):";

	$Input=<stdin>;
	chomp($Input);
	if ( $Input eq "q" ){
		last;
	}
	$Segmented=Segment($Input);
	print "$Segmented\n";
}

sub Segment
{
	my($ForSeg)=@_;
	my $Segmented="";
	while( length($ForSeg)> 0 ){
		for ( $Len=$MaxLen;$Len>0;$Len--){
				$ForMath=substr($ForSeg,0,$Len);
				if ( defined $mapDic{$ForMath}){
					$Segmented.=$ForMath;
					$Segmented.="/";
					$Matched=1;
					last
				}else{
					$Matched=0;
				}
		}
		if ( $Matched == 0 ){
			if ( ord($ForSeg) & 0x80 ){
				$Len=2;
			}else{
				$Len=1;
			}
			$Char=substr($ForSeg,0,$Len);
			$Segmented.=$Char;
			$Segmented.="/";
		}

		$ForSeg=substr($ForSeg,$Len,length($ForSeg)-$Len);
	}
	return $Segmented;
}