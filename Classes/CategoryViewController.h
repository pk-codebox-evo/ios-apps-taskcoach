//
//  CategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "BaseCategoryViewController.h"
#import "BonjourBrowser.h"
#import "SyncViewController.h"

@class NavigationController;

@interface CategoryViewController : BaseCategoryViewController <BonjourBrowserDelegate>
{
	NavigationController *navigationController;
	UIBarButtonItem *syncButton;
}

@property (nonatomic, assign) IBOutlet NavigationController *navigationController;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *syncButton;

- (IBAction)onAddCategory:(UIBarButtonItem *)button;
- (IBAction)onSynchronize:(UIBarButtonItem *)button;

@end
