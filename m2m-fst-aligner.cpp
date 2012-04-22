/*
    m2m-fst-aligner.cpp

    Copyright 2011-2012 Josef Robert Novak

    This file is part of Phonetisaurus.

    Phonetisaurus is free software: you can redistribute it 
    and/or modify it under the terms of the GNU General Public 
    License as published by the Free Software Foundation, either 
      version 3 of the License, or (at your option) any later version.

      Phonetisaurus is distributed in the hope that it will be useful, but 
      WITHOUT ANY WARRANTY; without even the implied warranty of 
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
    General Public License for more details.

    You should have received a copy of the GNU General Public 
    License along with Phonetisaurus. If not, see http://www.gnu.org/licenses/.
*/
#include "M2MFstAligner.hpp"
using namespace fst;


void split_string( string* input, vector<string>* tokens, string* delim ){
  //Standard C++ string splitter found all over the web.                                                          
  istringstream iss(*input);
  string token;
  while( getline(iss, token, *delim->c_str()) )
    tokens->push_back(token);
  return;
}

int main( int argc, char* argv[] ){
  M2MFstAligner fst_maker( false, true, 2, 2, "|", "|", "}", "<eps>", "_", true );
  ifstream infile(argv[1]);
  string line;
  string delim = "\t";
  string char_delim = " ";
  cout << "Loading..." << endl;
  if( infile.is_open() ){
    while( infile.good() ){
      getline(infile, line);
      if( line.empty() )
        continue;
      vector<string> tokens;
      split_string( &line, &tokens, &delim );
      vector<string> seq1;
      split_string( &tokens.at(0), &seq1, &char_delim );
      vector<string> seq2;
      split_string( &tokens.at(1), &seq2, &char_delim );
      fst_maker.entry2alignfst( seq1, seq2 );
    }
    infile.close();
  }
  
  cout << "Starting EM..." << endl;
  fst_maker.maximization(false);
  cout << "Finished first iter..." << endl;
  for( int i=1; i<=atoi(argv[3]); i++ ){
    cout << "ITERATION: " << i << endl;
    fst_maker.expectation();
    fst_maker.maximization(false);
  }
  cout << "ITERATION: 11" << endl;
  fst_maker.expectation();
  fst_maker.maximization(true);

  for( int i=0; i<fst_maker.fsas.size(); i++ ){
    for( int i=0; i<fst_maker.fsas.size(); i++ ){
      vector<PathData> paths = fst_maker.write_alignment( fst_maker.fsas[i], 1 );
      for( int i=0; i<paths.size(); i++ ){
	for( int j=0; j<paths[i].path.size(); j++ ){
	  cout << paths[i].path[j];
	  if( j<paths[i].path.size() )
	    cout << " ";
	}
	cout << endl;
      }
    }
  }
  
  return 1;
}