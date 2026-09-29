#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <iostream>
#include <set>
#include "cl_application.hpp"
using namespace std;

int main() {

	string root_name;
	cin >> root_name;
	if (root_name.find('.') != string::npos || root_name.find('/') != string::npos) {

		return 1;
	}
	cl_application ob_application(nullptr, root_name);
	if (ob_application.build_tree_objects()) {
		ob_application.exec_app();
	}

	cout << "FINISHED" << endl;

	return 0;
}
